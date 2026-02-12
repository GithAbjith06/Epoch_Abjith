from fastapi import FastAPI
from app.models import ReadmeRequest, ReadmeResponse
from app.readme_agent import generate_readme

app = FastAPI(title="README Generation Agent")

@app.get("/about")
def about():
    return {"message": "AI README Generation Agent"}

@app.post("/generate-readme", response_model=ReadmeResponse)
def generate_readme_api(payload: ReadmeRequest):
    readme = generate_readme(payload.project_path)
    return ReadmeResponse(readme=readme)
