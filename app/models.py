from pydantic import BaseModel

class ReadmeRequest(BaseModel):
    project_path: str

class ReadmeResponse(BaseModel):
    readme: str
