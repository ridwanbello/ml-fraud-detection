from pydantic import BaseModel, Field
from typing import Optional

class Items(BaseModel):
    userText: str = Field(description="The text entered by the user")
    # databaseText: str = Field(description="The text from the database of lists of fraudulent texts")

class Attribute(BaseModel):
    features: str = Field(description="The features entered by the user. Can be phone number, link or email, separated by comma if more than one")
  
class ItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True

