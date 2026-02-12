from pydantic import BaseModel
from typing import Optional


class ReadmeResponse(BaseModel):
    success: bool
    readme: Optional[str] = None
    project_path: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
