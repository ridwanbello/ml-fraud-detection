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

@app.post("/api/v1/predict1")
def predict_with_stopwords(item: Item):
    if len(item.userText.split()) < 4 or len(item.databaseText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    result = PlagiarismChecker(item.userText,item.databaseText)
    return {"percentage": result.get_rate()}

@app.post("/api/v1/predict2")
def predict_without_stopwords(item: Item):
    if len(item.userText.split()) < 4 or len(item.databaseText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    result = PlagiarismWithoutStopWords(item.userText,item.databaseText)
    return {"percentage": result.get_rate()}

