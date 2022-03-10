# Import fastapi library
from fastapi import Body, FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
#from sqlalchemy.orm import Session
#from .database import engine, SessionLocal
from urllib.request import urlopen
import time
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
    # initial = time.time()
    # lines = ""
    # databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
    # f = urlopen(databaseText)
    # for line in f:
    #     k = line.strip()
        # lines += " "+k.decode('utf-8')
    # response = requests.get('http://sojiare.com/privatedocs/Email_scams.txt')
    # response.encoding = "utf-8"
    # data = response.text
    # for line in data.split('\r\n'):
    #     lines += " "+line
    # final = time.time() - initial
    # return lines, final
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
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
    result = PlagiarismChecker(item.userText,databaseText)
    return {"percentage": result.get_rate()}

@app.post("/api/v1/predict2", responses=predict_responses2)
def predict_without_stopwords(item: Item = Body(..., examples=predict_examples)):
    if len(item.userText.split()) < 4 :
        raise HTTPException(status_code=404, detail="Text should not be less than 4 words")
    databaseText = "http://sojiare.com/privatedocs/Email_scams.txt"
    result = PlagiarismWithoutStopWords(item.userText,databaseText)
    return {"percentage": result.get_rate()}

# @app.post("/api/v1/prediction" )
# def fetch_data(db: Session = Depends(get_database_session)):
#         records = db.query(Item).all()
#         return records