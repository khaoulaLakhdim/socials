from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home():
    message = "hi baby"
    return message