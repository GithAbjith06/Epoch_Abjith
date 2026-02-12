from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.readme_agent import generate_project_readme, save_readme
from app.models import ReadmeRequest, ReadmeResponse
from app.config import MODEL_NAME

app = FastAPI(
    title="README Generator Agent",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
