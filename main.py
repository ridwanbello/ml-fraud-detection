# Import fastapi library
from fastapi import Body, FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
#from sqlalchemy.orm import Session
#from .database import engine, SessionLocal
from urllib.request import urlopen
import time, requests
from numpy import argmax
# Import my modules
from schemas import Item
#import models
from PlagiarismChecker import PlagiarismChecker
from PlagiarismWithoutStopWords import PlagiarismWithoutStopWords

app = FastAPI(
    title='SOJI API',
    description='API documentation for SOJI Fraud Detection App',
    version="0.1.0",
    debug=True)

# CORS Origin Middleware
origins = [
    "http://localhost:5000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#models.Base.metadata.create_all(bind=engine)
# Dependency
# def get_database_session():
#     db = None
#     try:
#         db = SessionLocal()
#         yield db
#     finally:
#         db.close()

# Routes
@app.get("/")
def root():
    return {"Hello": "World"}

predict_examples = {
    "body":{
        "value": {
            "userText": "Johnson Paul WESTERN UNION DIRECTOR Miami Florida",
        } 
    }
}

predict_responses1 = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "percentage": 58.620689655172406,
                    "text": "WESTERN UNION DIRECTOR",
                    "list": [
                        11.428571428571429,
                        0.0,
                        0.0,
                        5.830903790087463,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.2658227848101267,
                        7.758620689655173,
                        0.0,
                        2.941176470588235,
                        0.0,
                        0.0,
                        0.0,
                        8.333333333333332,
                        3.278688524590164,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        32.6530612244898,
                        36.0,
                        21.73913043478261,
                        36.0,
                        0.0,
                        0.0,
                        27.397260273972602,
                        0.0,
                        14.084507042253522,
                        0.0,
                        0.0,
                        6.993006993006993,
                        0.0,
                        2.5316455696202533,
                        0.0,
                        7.518796992481203,
                        0.0,
                        7.5,
                        7.547169811320755,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.1560693641618496,
                        0.0,
                        3.3333333333333335,
                    ]
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
                    "percentage": 58.620689655172406,
                    "text": "WESTERN UNION DIRECTOR",
                    "list": [
                        11.428571428571429,
                        0.0,
                        0.0,
                        5.830903790087463,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.2658227848101267,
                        7.758620689655173,
                        0.0,
                        2.941176470588235,
                        0.0,
                        0.0,
                        0.0,
                        8.333333333333332,
                        3.278688524590164,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        32.6530612244898,
                        36.0,
                        21.73913043478261,
                        36.0,
                        0.0,
                        0.0,
                        27.397260273972602,
                        0.0,
                        14.084507042253522,
                        0.0,
                        0.0,
                        6.993006993006993,
                        0.0,
                        2.5316455696202533,
                        0.0,
                        7.518796992481203,
                        0.0,
                        7.5,
                        7.547169811320755,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        1.1560693641618496,
                        0.0,
                        3.3333333333333335,
                    ]
                }
            }
        }
    }
}

def get_url_content_only(filename):
        response = requests.get(filename)
        response.encoding = "utf-8"
        data = response.text
        return data

@app.post("/api/v1/predict1", responses=predict_responses1)
def predict_with_stopwords(item: Item = Body(..., examples=predict_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=400, detail="Text should not be less than 4 words")
    databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
    data = get_url_content_only(databaseText)
    data = data.split('\r\n')
    results=[]
    for i, line in enumerate(data):
        result = PlagiarismChecker(item.userText,line)
        myresult = result.get_rate()
        results.append(myresult)
    max_value = max(results)
    max_index = results.index(max_value)
    return {"percentage": max_value, "text": data[max_index], "list": results}

@app.post("/api/v1/predict2", responses=predict_responses2)
def predict_without_stopwords(item: Item = Body(..., examples=predict_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=400, detail="Text should not be less than 4 words")
    databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
    data = get_url_content_only(databaseText)
    data = data.split('\r\n')
    results=[]
    for i, line in enumerate(data):
        result = PlagiarismWithoutStopWords(item.userText,line)
        myresult = result.get_rate()
        results.append(myresult)
    max_value = max(results)
    max_index = results.index(max_value)
    return {"percentage": max_value, "text": data[max_index], "list": results}

# @app.post("/api/v1/prediction" )
# def fetch_data(db: Session = Depends(get_database_session)):
#         records = db.query(Item).all()
#         return records