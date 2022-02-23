# Import fastapi library
from fastapi import FastAPI, HTTPException


# Import my modules
from models import Item
from PlagiarismChecker import PlagiarismChecker
from PlagiarismWithoutStopWords import PlagiarismWithoutStopWords

app = FastAPI()

@app.get("/")
def root():
    return {"Hello": "World"}

@app.get("/prediction")
def prediction():
    checker = PlagiarismChecker("I am a boy going to the market","I am a girl going to the market")
    return {"percentage": checker.get_rate()}

@app.post("/api/v1/predict1")
def predict(item: Item):
    if len(item.userText.split()) < 4 or len(item.databaseText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    result = PlagiarismChecker(item.userText,item.databaseText)
    return {"percentage": result.get_rate()}

@app.post("/api/v1/predict2")
def predict(item: Item):
    result = PlagiarismWithoutStopWords(item.userText,item.databaseText)
    return {"percentage": result.get_rate()}

