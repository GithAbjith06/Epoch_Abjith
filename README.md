AI README Generation Agent

This project implements an AI agent that generates a README file
for a given project directory.

The agent works in two stages:

1. Static analysis
   - Traverses the directory
   - Extracts Python functions, classes, and imports using AST
   - Builds a summary of project structure
   - Applies safety limits (file size, depth, file count)

2. README generation
   - Uses Gemini LLM
   - Generates a natural README based on the analysis

Safety limits:
- Maximum file size: 100KB
- Maximum files processed: 500
- Maximum directory depth: 10
- Files with syntax errors are skipped

Usage:
1. Create a .env file with GOOGLE_API_KEY
2. Install dependencies
3. Run: uvicorn app.__main__:app --reload
4. Use /generate-readme endpoint
