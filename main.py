import uvicorn
from fastapi import FastAPI
import os
from fastapi_sqlalchemy import DBSessionMiddleware
from src.endpoints import manager
from src.endpoints.glass import glassType, glassManufactures, glassManufacturePrices
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = FastAPI()
app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])
app.include_router(manager.router)
app.include_router(glassManufacturePrices.router)
app.include_router(glassType.router)
app.include_router(glassManufactures.router)

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
