import os
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS
from src.utils import format_structure_tree


@dataclass
class ReadmeConfig:
    IGNORED_DIRS: set = field(default_factory=lambda: {
        '__pycache__', 'venv', '.venv', '.env', '.git',
        'node_modules', 'dist', 'build'
    })
    MAX_FILE_SIZE: int = 100_000
    MAX_FILES_TOTAL: int = 500
    MAX_DEPTH: int = 10


@dataclass
class FileInfo:
    name: str
    extension: str
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)


@dataclass
class DirectoryNode:
    name: str
    files: List[FileInfo] = field(default_factory=list)
    subdirs: Dict[str, 'DirectoryNode'] = field(default_factory=dict)


class ProjectAnalyzer:

    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.config = ReadmeConfig()
        self.root_node = DirectoryNode(name=self.root.name)
        self.summary = {
            "total_files": 0,
            "file_types": {},
            "functions": [],
            "classes": [],
            "dependencies": set()
        }

    def analyze(self):
        self._traverse(self.root, self.root_node)
        return {
            "project_name": self.root.name,
            "structure": self._serialize_node(self.root_node),
            "summary": self.summary
        }

    def _traverse(self, path: Path, node: DirectoryNode, depth=0):
        if depth > self.config.MAX_DEPTH:
            return

        for item in path.iterdir():
            if item.name.startswith("."):
                continue

            if item.is_dir():
                if item.name in self.config.IGNORED_DIRS:
                    continue
                subdir = DirectoryNode(name=item.name)
                node.subdirs[item.name] = subdir
                self._traverse(item, subdir, depth + 1)

            elif item.is_file():
                if item.stat().st_size > self.config.MAX_FILE_SIZE:
                    continue

                file_info = self._analyze_file(item)
                if file_info:
                    node.files.append(file_info)
                    self._update_summary(file_info)

    def _analyze_file(self, file_path: Path):
        info = FileInfo(
            name=file_path.name,
            extension=file_path.suffix or "no_ext"
        )

        self.summary["total_files"] += 1
        self.summary["file_types"][info.extension] = \
            self.summary["file_types"].get(info.extension, 0) + 1

        if file_path.suffix == ".py":
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
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

            except Exception:
                pass

        return info

    def _update_summary(self, file_info):
        self.summary["functions"].extend(file_info.functions)
        self.summary["classes"].extend(file_info.classes)
        self.summary["dependencies"].update(file_info.imports)

    def _serialize_node(self, node: DirectoryNode):
        return {
            "name": node.name,
            "files": [{"name": f.name} for f in node.files],
            "subdirs": {
                name: self._serialize_node(sub)
                for name, sub in node.subdirs.items()
            }
        }


class ReadmeGenerator:

    def __init__(self, analysis):
        self.analysis = analysis
        self.llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS
        )

    def generate(self):
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "Write a clear, professional README.md for the given project analysis."),
            ("human",
             "Project Name: {project_name}\n"
             "Total Files: {total_files}\n"
             "File Types: {file_types}\n"
             "Functions: {functions}\n"
             "Classes: {classes}\n"
             "Dependencies: {dependencies}\n"
             "Structure:\n{structure}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        return chain.invoke({
            "project_name": self.analysis["project_name"],
            "total_files": self.analysis["summary"]["total_files"],
            "file_types": str(self.analysis["summary"]["file_types"]),
            "functions": str(self.analysis["summary"]["functions"]),
            "classes": str(self.analysis["summary"]["classes"]),
            "dependencies": str(list(self.analysis["summary"]["dependencies"])),
            "structure": format_structure_tree(self.analysis["structure"])
        })


def generate_project_readme(project_path: str):
    analyzer = ProjectAnalyzer(project_path)
    analysis = analyzer.analyze()
    generator = ReadmeGenerator(analysis)
    readme = generator.generate()

    return {
        "success": True,
        "readme": readme,
        "project_path": project_path
    }
