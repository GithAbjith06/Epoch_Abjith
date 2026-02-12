# README Generator Agent

An AI-powered system that automatically generates a professional `README.md` file from a project ZIP upload.

Built using FastAPI and Google Gemini.

---

## Overview

This application analyzes a project structure by extracting an uploaded ZIP file, inspecting its contents, and generating a structured README file using a Large Language Model.

The system focuses only on README generation and does not include docstring generation.

---

## Features

- Upload a project as a ZIP file
- Automatic directory traversal and structure analysis
- Python AST parsing for:
  - Functions
  - Classes
  - Imports
- Dependency detection from import statements
- File type summary
- Structured project tree visualization
- AI-generated README using Google Gemini
- Temporary extraction with automatic cleanup
- Clean and minimal web interface

---

## How It Works

1. User uploads a project ZIP file.
2. The server extracts it into a temporary directory.
3. The project is analyzed:
   - File structure is mapped.
   - Python files are parsed using `ast`.
   - Functions, classes, and imports are collected.
4. The collected metadata is sent to Gemini.
5. Gemini generates a structured `README.md`.
6. Temporary files are deleted.

No uploaded code is executed at any point.

---

## Project Structure

Epoch_Abjith/
├── app/
│ ├── init.py
│ ├── main.py
│ ├── config.py
│ ├── models.py
│ ├── readme_agent.py
│ ├── utils.py
│ ├── static/
│ │ └── styles.css
│ └── templates/
│ └── index.html
├── requirements.txt
└── README.md


---

## Installation

### 1. Clone the repository

git clone <your-repo-url>
cd Epoch_Abjith


### 2. Create virtual environment

python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Linux/Mac)


### 3. Install dependencies

pip install -r requirements.txt


### 4. Set your API key

Create a `.env` file in the project root:

GOOGLE_API_KEY=your_gemini_api_key


---

## Running the Application

From inside the project root:

uvicorn app.main:app --reload


Open in browser:

http://127.0.0.1:8000


---

## API Endpoints

### Health Check

GET /health


Returns server status and model name.

---

### Upload ZIP & Generate README

POST /api/upload-zip


Form-data:
zip_file: project.zip


Returns:

{
"success": true,
"readme": "...generated markdown...",
"project_path": "temporary_path"
}


---

## Safety Measures

- Maximum file size limit (100 KB per file)
- Maximum traversal depth (10 levels)
- Hidden folders ignored
- Virtual environments ignored
- ZIP file validation
- Corrupted ZIP detection
- Temporary directory cleanup
- No code execution
- AST parsing only

---

## Assumptions & Limitations

- Designed primarily for Python projects.
- Only `.py` files are deeply analyzed.
- Large projects (>500 files) may be partially analyzed.
- Generated README quality depends on LLM output.

---

## Edge Cases Handled

- Empty ZIP files
- Corrupted ZIP uploads
- Projects with nested folders
- Hidden files
- Syntax errors in Python files
- Permission errors
- Non-Python projects (basic structural README generated)

---

## Technology Stack

- FastAPI
- Google Gemini (gemini-2.5-flash)
- LangChain
- Python AST
- Jinja2
- Vanilla HTML/CSS

---

## License

MIT License