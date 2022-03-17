from pydantic import BaseModel, Field


class Item(BaseModel):
    userText: str = Field(description="The text entered by the user")
    # databaseText: str = Field(description="The text from the database of lists of fraudulent texts")

class Attribute(BaseModel):
    features: str = Field(description="The features entered by the user. Can be phone number, link or email, separated by comma if more than one")
    