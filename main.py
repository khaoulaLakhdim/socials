from fastapi import FastAPI
from contextlib import asynccontextmanager
from database import db_init
import models

@asynccontextmanager
async def lifespan(app : FastAPI):
    db_init()
    yield

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    message = "hi baby"
    return message


