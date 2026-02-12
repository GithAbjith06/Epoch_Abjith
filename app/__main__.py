import os
import shutil
import tempfile
import zipfile
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.readme_agent import generate_project_readme
from app.config import MODEL_NAME


app = FastAPI(title="README Generator Agent", version="1.0.0")

# 🔥 Absolute path fix
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static"
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model": MODEL_NAME
    }


@app.post("/api/upload-zip")
async def upload_zip(zip_file: UploadFile = File(...)):

    if not zip_file.filename.endswith(".zip"):
        return {"success": False, "error": "Only ZIP files allowed."}

    temp_dir = tempfile.mkdtemp()

    try:
        zip_path = os.path.join(temp_dir, zip_file.filename)

        with open(zip_path, "wb") as buffer:
            buffer.write(await zip_file.read())

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        result = generate_project_readme(temp_dir)
        return result

    except zipfile.BadZipFile:
        return {"success": False, "error": "Invalid ZIP file."}

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
