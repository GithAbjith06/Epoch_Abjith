# README Generator Agent

An AI-based agent that automatically generates a comprehensive `README.md` file for any project directory.

The system combines deterministic static analysis with LLM-based documentation generation to produce structured, human-readable README files.

---

## Overview

This agent analyzes a project folder, extracts structural and metadata information, and generates a complete README using Google Gemini via LangChain.

It is designed to avoid simply sending raw files to a language model. Instead, it performs structured analysis first, then synthesizes documentation from extracted metadata.

---

## Architecture

The system follows a two-stage pipeline:

### 1. Static Analysis Stage

- Recursively traverses the project directory
- Builds a nested directory structure tree
- Extracts Python functions, classes, and imports using AST
- Detects dependencies
- Tracks file types and line counts
- Applies strict safety limits:
  - Maximum 500 files
  - Maximum depth of 10
  - Maximum file size of 100 KB

### 2. README Generation Stage

- Sends structured metadata to Google Gemini
- Uses a controlled prompt to generate natural documentation
- Produces a clean Markdown README
- Validates output before returning

---

## Features

- Nested directory tree generation
- Python AST-based metadata extraction
- Dependency detection from imports
- File type analysis
- Safety limits for large projects
- CLI support
- FastAPI REST API support
- Option to save README directly to disk

---

## Installation

1. Clone the repository.
2. Install dependencies:

