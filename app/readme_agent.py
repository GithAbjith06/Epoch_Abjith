import os
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS
from app.utils import format_structure_tree


# =====================================================
# Configuration
# =====================================================
@dataclass
class ReadmeConfig:
    IGNORED_DIRS: set = field(default_factory=lambda: {
        '__pycache__', 'venv', 'env', '.venv', '.env', '.git',
        'node_modules', 'dist', 'build', '.pytest_cache',
        '.mypy_cache', '.ruff_cache', '.idea', '.vscode'
    })
    MAX_FILE_SIZE: int = 100_000
    MAX_FILES_TOTAL: int = 500
    MAX_DEPTH: int = 10
    MAX_DEPENDENCIES: int = 30
    MAX_FUNCTIONS: int = 50
    MAX_CLASSES: int = 30


@dataclass
class FileInfo:
    path: str
    name: str
    extension: str
    size: int
    line_count: int
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


@dataclass
class DirectoryNode:
    name: str
    path: str
    files: List[FileInfo] = field(default_factory=list)
    subdirs: Dict[str, 'DirectoryNode'] = field(default_factory=dict)


# =====================================================
# Project Analyzer
# =====================================================
class ProjectAnalyzer:

    def __init__(self, root_path: str, config: ReadmeConfig = None):
        self.root = Path(root_path)
        self.config = config or ReadmeConfig()
        self.root_node = DirectoryNode(name=self.root.name, path=str(self.root))
        self.summary = {
            "total_files": 0,
            "total_dirs": 0,
            "file_types": {},
            "functions": [],
            "classes": [],
            "dependencies": set(),
            "total_lines": 0,
            "skipped_files": 0
        }
        self.file_count = 0
        self.stop_traversal = False

    def analyze(self) -> Dict[str, Any]:

        if not self.root.exists() or not self.root.is_dir():
            raise ValueError(f"Invalid project directory: {self.root}")

        self._traverse(self.root, self.root_node)

        self.summary["dependencies"] = \
            list(self.summary["dependencies"])[:self.config.MAX_DEPENDENCIES]

        self.summary["functions"] = \
            self.summary["functions"][:self.config.MAX_FUNCTIONS]

        self.summary["classes"] = \
            self.summary["classes"][:self.config.MAX_CLASSES]

        return {
            "project_name": self.root.name,
            "root_path": str(self.root.absolute()),
            "structure": self._serialize_node(self.root_node),
            "summary": self.summary
        }

    def _traverse(self, current_path: Path, node: DirectoryNode, depth: int = 0):

        if self.stop_traversal:
            return

        if depth > self.config.MAX_DEPTH:
            return

        if self.file_count >= self.config.MAX_FILES_TOTAL:
            self.stop_traversal = True
            return

        try:
            for item in sorted(current_path.iterdir()):

                if self.stop_traversal:
                    return

                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    if item.name in self.config.IGNORED_DIRS:
                        continue

                    dir_node = DirectoryNode(
                        name=item.name,
                        path=str(item.relative_to(self.root))
                    )
                    node.subdirs[item.name] = dir_node
                    self.summary["total_dirs"] += 1
                    self._traverse(item, dir_node, depth + 1)

                else:
                    if self.file_count >= self.config.MAX_FILES_TOTAL:
                        self.stop_traversal = True
                        return

                    try:
                        size = item.stat().st_size
                    except Exception:
                        continue

                    if size > self.config.MAX_FILE_SIZE:
                        self.summary["skipped_files"] += 1
                        continue

                    self.file_count += 1
                    file_info = self._analyze_file(item)

                    if file_info:
                        node.files.append(file_info)
                        self._update_summary(file_info)

        except PermissionError:
            pass

    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:

        try:
            rel_path = str(file_path.relative_to(self.root))

            info = FileInfo(
                path=rel_path,
                name=file_path.name,
                extension=file_path.suffix or "no_ext",
                size=file_path.stat().st_size,
                line_count=0
            )

            if file_path.suffix == ".py":
                try:
                    content = file_path.read_text(
                        encoding="utf-8",
                        errors="ignore"
                    )
                except Exception:
                    return info

                info.line_count = len(content.splitlines())

                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):

                        if isinstance(node, ast.FunctionDef):
                            info.functions.append(node.name)

                        elif isinstance(node, ast.ClassDef):
                            info.classes.append(node.name)

                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                info.imports.append(alias.name)

                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                info.imports.append(node.module)

                except SyntaxError:
                    pass

            return info

        except Exception:
            return None

    def _update_summary(self, file_info: FileInfo):

        ext = file_info.extension
        self.summary["file_types"][ext] = \
            self.summary["file_types"].get(ext, 0) + 1

        self.summary["total_lines"] += file_info.line_count
        self.summary["functions"].extend(file_info.functions)
        self.summary["classes"].extend(file_info.classes)
        self.summary["dependencies"].update(file_info.imports)

    def _serialize_node(self, node: DirectoryNode) -> Dict:

        return {
            "name": node.name,
            "files": [{"name": f.name} for f in node.files],
            "subdirs": {
                name: self._serialize_node(sub)
                for name, sub in node.subdirs.items()
            }
        }


# =====================================================
# README Generator
# =====================================================
class ReadmeGenerator:

    def __init__(self, analysis: Dict[str, Any]):
        self.analysis = analysis
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

    def generate(self) -> str:

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             """You are an experienced software engineer writing documentation.

Based on the structured project analysis, write a clear and practical README.md.

Explain:
- What the project does
- Its main components
- How to install and use it
- The project structure
- Dependencies if relevant
- Assumptions or limitations
- Edge cases handled

Write naturally and professionally using Markdown headings.
"""),
            ("human",
             """Project Analysis:
Name: {project_name}
Root: {root_path}
Total files: {total_files}
Total directories: {total_dirs}
File types: {file_types}
Total lines: {total_lines}
Functions: {functions_count}
Classes: {classes_count}
Dependencies: {dependencies}

Project Structure:
{structure}

Generate the README now.
""")
        ])

        chain = prompt | self.llm | StrOutputParser()

        readme = chain.invoke({
            "project_name": self.analysis["project_name"],
            "root_path": self.analysis["root_path"],
            "total_files": self.analysis["summary"]["total_files"],
            "total_dirs": self.analysis["summary"]["total_dirs"],
            "file_types": ", ".join(
                f"{k}:{v}"
                for k, v in self.analysis["summary"]["file_types"].items()
            ),
            "total_lines": self.analysis["summary"]["total_lines"],
            "functions_count": len(self.analysis["summary"]["functions"]),
            "classes_count": len(self.analysis["summary"]["classes"]),
            "dependencies": ", ".join(
                self.analysis["summary"]["dependencies"]
            ) or "none",
            "structure": format_structure_tree(self.analysis["structure"])
        })

        if not readme or len(readme.strip()) < 50:
            raise ValueError("Generated README appears invalid.")

        return readme


# =====================================================
# Public Functions
# =====================================================
def generate_project_readme(project_path: str) -> Dict[str, Any]:

    try:
        analyzer = ProjectAnalyzer(project_path)
        analysis = analyzer.analyze()

        generator = ReadmeGenerator(analysis)
        readme = generator.generate()

        return {
            "success": True,
            "readme": readme,
            "project_path": os.path.abspath(project_path),
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "readme": None,
            "project_path": project_path,
            "error": str(e)
        }


def save_readme(project_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:

    result = generate_project_readme(project_path)

    if not result["success"]:
        return result

    save_path = Path(output_path) if output_path else Path(project_path) / "README.md"

    try:
        save_path.write_text(result["readme"], encoding="utf-8")
    except Exception as e:
        return {
            "success": False,
            "readme": None,
            "project_path": project_path,
            "error": str(e)
        }

    result["message"] = f"README saved to {save_path}"
    result["file_path"] = str(save_path)

    return result
