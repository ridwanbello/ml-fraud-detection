# Import fastapi library
from dataclasses import replace
from typing import List
from unittest import result
from fastapi import Body, FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from urllib.request import urlopen
import time, requests
from numpy import argmax
# Import my modules
from schemas import Items, Attribute, User
import crud, models, schemas
#import models

from sqlalchemy.orm.session import Session
from PlagiarismChecker import PlagiarismChecker
from PlagiarismWithoutStopWords import PlagiarismWithoutStopWords

app = FastAPI(
    title='SOJI API',
    description='API documentation for SOJI Fraud Detection App',
    version="0.1.0",
    debug=True)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CORS Origin Middleware
origins = [
    "*",
    "http://localhost:5000",
    "http://localhost:3000",
    "https://sojiare.com",
    "https://sojiare.org",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
def predict_with_stopwords(item: Items = Body(..., examples=text_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=400, detail="Text should not be less than 4 words")
    try:    
        databaseText = "https://justicelab.io/privatedocs/Email_scams.txt"
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
def predict_without_stopwords(item: Items = Body(..., examples=text_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=400, detail="Text should not be less than 4 words")
    try:
        databaseText = "https://justicelab.io/privatedocs/Email_scams.txt"
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
        attributeTxt = get_url_content_only("https://justicelab.io/privatedocs/scamPhones.txt")
        attributeList = attributeTxt.split('\r\n')
        attributeSet = set(attributeList)
        results = []
        data = attribute.features
    except:
        raise HTTPException(status_code=500, detail="Server error")
    splittedData = data.split(',')
    cleanedData=""
    if len(splittedData) > 1 :
        for i, e in enumerate(splittedData):
            conversion = convert_to_international(e)
            if(conversion[0]=="+"):
                validation = check_valid_number(conversion)
                if(len(validation) > 1):
                    raise HTTPException(status_code=400, detail=validation)
            cleanedData = conversion
            if cleanedData in attributeSet:
                results.append(cleanedData)
    else :
        conversion = convert_to_international(data)
        if(conversion[0]=="+"):
            validation = check_valid_number(conversion)
            if(len(validation) > 1):
                raise HTTPException(status_code=400, detail=validation)
        cleanedData = conversion
        if cleanedData in attributeSet:
            results.append(cleanedData)
    return {"matched": results}

@app.post("/api/v1/check_attribute_with_text", responses=check_responses)
def check_attribute_with_text(attribute: Attribute = Body(..., examples=check_examples)):
    try:
        attributeTxt = get_url_content_only("https://justicelab.io/privatedocs/scamPhones.txt")
        wordTxt = get_url_content_only("https://justicelab.io/privatedocs/Email_scams.txt")
        attributeList = attributeTxt.split('\r\n')
        attributeSet = set(attributeList)
        wordList = wordTxt.split('\r\n')
        results = []
        data = attribute.features
    except:
        raise HTTPException(status_code=500, detail="Server error")
    splittedData = data.split(',')
    cleanedData=""
    if len(splittedData) > 1 :
        for i, e in enumerate(splittedData):
            conversion = convert_to_international(e)
            if(conversion[0]=="+"):
                validation = check_valid_number(conversion)
                if(len(validation) > 1):
                    raise HTTPException(status_code=400, detail=validation)
            cleanedData = conversion
            if cleanedData in attributeSet:
                results.append(cleanedData)
            for i, e in enumerate(wordList):
                for k in e.split(" "):
                    if cleanedData in k:
                        results.append(cleanedData)    
    else :
        conversion = convert_to_international(data)
        if(conversion[0]=="+"):
            validation = check_valid_number(conversion)
            if(len(validation) > 1):
                raise HTTPException(status_code=400, detail=validation)
        cleanedData = conversion
        if cleanedData in attributeSet:
            results.append(cleanedData)
        for i, e in enumerate(wordList):
            for k in e.split(" "):
                if cleanedData in k:
                    results.append(cleanedData)
    return {"matched": results}

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    
    for i, data in enumerate(users):
        yield data.email


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items