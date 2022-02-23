# Import fastapi library
from fastapi import Body, FastAPI, HTTPException


# Import my modules
from models import Item
from PlagiarismChecker import PlagiarismChecker
from PlagiarismWithoutStopWords import PlagiarismWithoutStopWords

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

predict_examples = {
    "body":{
        "value": {
            "userText": "This is a string that is entered by the user",
            "databaseText": "This is a string that is coming from the database"
        } 
    }
}

predict_responses1 = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "percentage": "37.5"
                }
            }
        }
    }
}

predict_responses2 = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "percentage": "48.38"
                }
            }
        }
    }
}

@app.post("/api/v1/predict1", responses=predict_responses1)
def predict_with_stopwords(item: Item = Body(..., examples=predict_examples)):
    if len(item.userText.split()) < 4 or len(item.databaseText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    result = PlagiarismChecker(item.userText,item.databaseText)
    return {"percentage": result.get_rate()}

@app.post("/api/v1/predict2", responses=predict_responses2)
def predict_without_stopwords(item: Item = Body(..., examples=predict_examples)):
    if len(item.userText.split()) < 4 or len(item.databaseText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    result = PlagiarismWithoutStopWords(item.userText,item.databaseText)
    return {"percentage": result.get_rate()}

