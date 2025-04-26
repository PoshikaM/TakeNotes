from pydantic import BaseModel

class Notes(BaseModel):
    title : str
    content : str

class User(BaseModel):
    email : str
    password : str