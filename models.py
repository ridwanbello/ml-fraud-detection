from pydantic import BaseModel, Field


class Item(BaseModel):
    userText: str = Field(description="The text entered by the user")
    databaseText: str = Field(description="The text from the database of lists of fraudulent texts")
    