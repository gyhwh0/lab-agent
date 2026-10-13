from pydantic import BaseModel

class FileResonse(BaseModel):
    original_name:str
    disk_name:str
    size:int
    url:str
