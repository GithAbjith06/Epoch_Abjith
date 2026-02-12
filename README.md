# README Generator Agent

An AI-based agent that automatically generates a complete `README.md` file for a given project directory.

The system analyzes the project structure, extracts metadata, and uses a language model to produce structured documentation.

---

## Overview

This project implements a README generation agent that combines deterministic static analysis with LLM-based documentation synthesis.

Instead of sending raw project files directly to a language model, the system first performs structured analysis. It then uses the extracted metadata to generate a clear and organized README file.

This approach improves reliability, reduces noise, and makes the output more consistent.

---

## How It Works

The system operates in two stages:

### 1. Static Analysis

The agent:

- Recursively traverses the project directory  
- Builds a nested directory structure tree  
- Extracts Python functions, classes, and imports using `ast`  
- Detects dependencies  
- Tracks file types and total lines of code  
- Applies strict safety limits  

Safety limits include:

- Maximum 500 files processed  
- Maximum directory depth of 10  
- Maximum file size of 100 KB  
- Ignoring hidden and common cache/build directories  

### 2. README Generation

After analysis, structured metadata is passed to Google Gemini via LangChain.

A controlled prompt is used to generate a human-readable README that typically includes:

- Project overview  
- Key features  
- Installation instructions  
- Usage guidance  
- Project structure  
- Dependencies  
- Assumptions and limitations  
- Edge case handling  

The output is validated before being returned or saved.

---

## Features

- Recursive project traversal  
- Nested directory tree generation  
- Python AST-based metadata extraction  
- Dependency detection from import statements  
- File type summary  
- CLI interface  
- FastAPI REST API  
- Option to save README directly to disk  
- Safety limits for large or complex repositories  

---

## Installation

1. Clone the repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
MODEL_NAME=gemini-1.5-flash
TEMPERATURE=0.2
MAX_TOKENS=2048
```

---

## Usage

### Command Line

Generate and print README:

```bash
python -m app.cli readme /path/to/project
```

Generate and save to disk:

```bash
python -m app.cli readme /path/to/project --save
```

Save to a custom file:

```bash
python -m app.cli readme /path/to/project --save --output ./custom_readme.md
```

---

### API Server

Start the server:

```bash
uvicorn app.api:app --reload
```

Available endpoints:

- `GET /health` — Service health check  
- `POST /api/readme` — Generate README  
- `POST /api/readme/save` — Generate and save README  

Example request:

```bash
curl -X POST http://localhost:8000/api/readme \
  -H "Content-Type: application/json" \
  -d '{"project_path": "/path/to/project"}'
```

---

## Assumptions and Limitations

- Only Python files are parsed for functions, classes, and imports.  
- Files larger than 100 KB are skipped.  
- Maximum 500 files and depth 10 are processed.  
- Binary files and hidden directories are ignored.  
- Internet access is required for Gemini API.  
- Output quality depends on extracted metadata and model response.  

---

## Edge Cases Handled

- Empty directories  
- Permission errors  
- Syntax errors in Python files  
- Large files exceeding size limit  
- Deeply nested directory structures  
- Hidden and cache folders  
- Projects without Python code  

---

## Purpose

This project demonstrates how structured static analysis can be combined with large language models to automate documentation generation in a controlled and reliable way.
