from pydantic import BaseModel
from typing import Optional


class ReadmeRequest(BaseModel):
    project_path: str


class ReadmeResponse(BaseModel):
    success: bool
    readme: Optional[str] = None
    project_path: str
    message: Optional[str] = None
    error: Optional[str] = None
