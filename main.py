# Import fastapi library
from dataclasses import replace
from unittest import result
from fastapi import Body, FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
#from sqlalchemy.orm import Session
#from .database import engine, SessionLocal
from urllib.request import urlopen
import time, requests
from numpy import argmax
# Import my modules
from schemas import Item, Attribute
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

text_examples = {
    "body":{
        "value": {
            "userText": "Johnson Paul WESTERN UNION DIRECTOR Miami Florida",
        } 
    }
}

text_responses = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "percentage": 58.620689655172406,
                    "text": "WESTERN UNION DIRECTOR",
                    "frequency": 23
                }
            }
        }
    },
    400:{
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Text should not be less than 4 words"
                }
            }
        }
    },
    500:{
        "description": "Server Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Server Error"
                }
            }
        }
    }
}


check_examples = {
    "body":{
        "value": {
            "features": "08034343434,+120324434",
        } 
    }
}

check_responses = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "matched": ["+2347014392964"]
                }
            }
        }
    },
    400:{
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Phone Number not valid. Please check and try again"
                }
            }
        }
    },
    500:{
        "description": "Server Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Server Error"
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

def convert_to_international(str):
    convertedStr = ""
    if(str[0] == "0"):
        convertedStr = str.replace(str[0], "+234", 1)
    elif(str[0:3] == "234"):
        convertedStr = str.replace(str[0:3], "+234", 1)
    else:
        convertedStr = str
    return convertedStr

def check_valid_number(phone):
    phoneLength = len(phone)
    if(phoneLength < 12 or phoneLength > 14):
        return "Phone Number not valid. Please check and try again"
    else:
        return ""

def find_occurences(data, phoneText):
    setPhoneText = set(phoneText)
    if(data in setPhoneText):
        return data

def clean_data(e):
    convertedData = convert_to_international(e)
    validation = check_valid_number(convertedData)
    if(len(validation) > 1):
        raise HTTPException(status_code=400, detail=validation)
    return convertedData



@app.post("/api/v1/predict1", responses=text_responses)
def predict_with_stopwords(item: Item = Body(..., examples=text_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=400, detail="Text should not be less than 4 words")
    try:    
        databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
        data = get_url_content_only(databaseText)
        data = data.split('\r\n')
    except:
        raise HTTPException(status_code=500, detail="Server error")
    results=[]
    for i, line in enumerate(data):
        result = PlagiarismChecker(item.userText,line)
        myresult = result.get_rate()
        results.append(myresult)
    max_value = max(results)
    max_index = results.index(max_value)
    frequency = sum(i > 0 for i in results)

    return {"percentage": max_value, "text": data[max_index], "frequency": frequency}

@app.post("/api/v1/predict2", responses=text_responses)
def predict_without_stopwords(item: Item = Body(..., examples=text_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=400, detail="Text should not be less than 4 words")
    try:
        databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
        data = get_url_content_only(databaseText)
        data = data.split('\r\n')
    except:
        raise HTTPException(status_code=500, detail="Server error")
    results=[]
    for i, line in enumerate(data):
        result = PlagiarismWithoutStopWords(item.userText,line)
        myresult = result.get_rate()
        results.append(myresult)
    max_value = max(results)
    max_index = results.index(max_value)
    frequency = sum(i > 0 for i in results)
    return {"percentage": max_value, "text": data[max_index], "frequency": frequency}

@app.post("/api/v1/check_attribute", responses=check_responses)
def check_attribute(attribute: Attribute = Body(..., examples=check_examples)):
    try:
        attributeTxt = get_url_content_only("http://sojiare.com/privatedocs/scamPhones.txt")
        attributeList = attributeTxt.split('\r\n')
        attributeSet = set(attributeList)
        results = []
        data = attribute.features
    except:
        raise HTTPException(status_code=500, detail="Server error")
    splittedData = data.split(',')
    if len(splittedData) > 1 :
        for i, e in enumerate(splittedData):
            cleanedData = clean_data(e)
            if cleanedData in attributeSet:
                results.append(cleanedData)
    else :
        cleanedData = clean_data(data)
        if cleanedData in attributeSet:
            results.append(cleanedData)
    return {"matched": results}

@app.post("/api/v1/check_attribute_with_text", responses=check_responses)
def check_attribute_with_text(attribute: Attribute = Body(..., examples=check_examples)):
    try:
        attributeTxt = get_url_content_only("http://sojiare.com/privatedocs/scamPhones.txt")
        wordTxt = get_url_content_only("http://sojiare.com/privatedocs/Email_scams.txt")
        attributeList = attributeTxt.split('\r\n')
        attributeSet = set(attributeList)
        wordList = wordTxt.split('\r\n')
        results = []
        data = attribute.features
    except:
        raise HTTPException(status_code=500, detail="Server error")
    splittedData = data.split(',')
    if len(splittedData) > 1 :
        for i, e in enumerate(splittedData):
            cleanedData = clean_data(e)
            if cleanedData in attributeSet:
                results.append(cleanedData)
            for i, e in enumerate(wordList):
                for k in e.split(" "):
                    if cleanedData in k:
                        results.append(cleanedData)    
    else :
        cleanedData = clean_data(data)
        if cleanedData in attributeSet:
            results.append(cleanedData)
        for i, e in enumerate(wordList):
            for k in e.split(" "):
                if cleanedData in k:
                    results.append(cleanedData)
    return {"matched": results}

