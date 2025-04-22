from pydantic import BaseModel
from typing import List

class UserPage(BaseModel):
    id: str
    telegram_id: int
    first_name: str
    last_name: str
    role: str
    subscriptions: List[str]   # lista di ClassPage.id
    waiting_list: List[str]    # lista di ClassPage.id

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class ClassPage(BaseModel):
    id: str
    name: str
    date: str
    time: str
    location: str
    capacity: int
    spots_left: int
    subscriptions: List[str]    # lista di UserPage.id
    waiting_list: List[str]     # lista di UserPage.id
    subscribers_count: int      # numero di iscritti
    waiting_count: int          # numero in lista d’attesa
