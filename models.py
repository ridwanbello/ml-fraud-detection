from pydantic import BaseModel


class Item(BaseModel):
    userText: str
    databaseText: str
    