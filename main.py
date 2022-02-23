# Import fastapi library
from fastapi import Body, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import my modules
from models import Item
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


# Routes
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

