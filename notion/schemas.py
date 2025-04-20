from pydantic import BaseModel

class UserPage(BaseModel):
    id: str
    telegram_id: int
    role: str

class ClassPage(BaseModel):
    id: str
    name: str
    time: str
    date: str
    location: str
    spots_left: int