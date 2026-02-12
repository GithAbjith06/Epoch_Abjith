from fastapi import FastAPI
from app.readme_agent import generate_project_readme, save_readme
from app.models import ReadmeRequest, ReadmeResponse
from app.config import MODEL_NAME

app = FastAPI(
    title="README Generator Agent",
    version="1.0.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": app.title,
        "version": app.version,
        "model": MODEL_NAME
    }


@app.post("/api/generate-readme", response_model=ReadmeResponse)
def api_generate_readme(req: ReadmeRequest):
    return generate_project_readme(req.project_path)


@app.post("/api/readme/save", response_model=ReadmeResponse)
def api_save_readme(req: ReadmeRequest):
    return save_readme(req.project_path)
