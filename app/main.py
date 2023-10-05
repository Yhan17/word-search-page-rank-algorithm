from fastapi import FastAPI, UploadFile
from app.function_utils import *
from app.query import *



app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World again"}

@app.get("/database")
async def database():
    connection_return = await connect_to_db()
    return {"status": connection_return}


@app.post("/search")
async def search_words(payload: Payload):
    results = weights_search(payload.words, payload)
    return results
