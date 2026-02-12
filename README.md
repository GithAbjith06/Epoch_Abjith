# README Generator Agent

An AI-powered system that automatically generates a professional `README.md` file from a project ZIP upload.

Built using FastAPI and Google Gemini.

---

## Overview

This application analyzes a project structure by extracting an uploaded ZIP file, inspecting its contents, and generating a structured README file using a Large Language Model.

The system focuses only on README generation.

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
- Clean minimal web interface

---

## Project Structure

Epoch_Abjith/
├── src/
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
├── Dockerfile
├── docker-compose.yml
└── README.md


---

## Installation

### 1. Clone the repository

git clone <your-repo-url>
cd Epoch_Abjith


### 2. Create virtual environment

python -m venv venv
venv\Scripts\activate


### 3. Install dependencies

pip install -r requirements.txt


### 4. Set your API key

Create a `.env` file:

GOOGLE_API_KEY=your_gemini_api_key


---

## Running the Application (Local)

uvicorn src.main:app --reload


Open:

http://127.0.0.1:8000


---

## Running with Docker

### Build

docker compose build


### Run

docker compose up


Application will be available at:

http://localhost:8000


---

## API Endpoints

### Health Check

GET /health


### Upload ZIP & Generate README

POST /api/upload-zip


Form-data:
zip_file: project.zip


---

## Safety Measures

- ZIP validation
- Temporary directory cleanup
- File size limits
- Depth limits
- Hidden directory skipping
- No code execution
- AST-based analysis only

---

## Assumptions & Limitations

- Designed primarily for Python projects.
- Only `.py` files are deeply analyzed.
- Generated README quality depends on LLM output.
- Large projects may be partially analyzed.

---

## Technology Stack

- FastAPI
- Google Gemini (gemini-2.5-flash)
- LangChain
- Python AST
- Jinja2
- Docker

---

## License

MIT License