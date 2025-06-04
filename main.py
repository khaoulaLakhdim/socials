from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from database import db_init, get_session
from models import User, Post,user_post
from sqlmodel import Session
from pydantic import BaseModel
@asynccontextmanager
async def lifespan(app : FastAPI):
    db_init()
    yield

class UserBase(BaseModel):
    name: str
    email: str

app = FastAPI(lifespan=lifespan)


@app.post("/users/")
def add_user(user: UserBase,session: Session = Depends(get_session)):
    #we need to check if the email already exist
    to_check = session.get(User,user.email)
    if not to_check:
        toadd = User(name = user.name, email = user.email)
        session.add(toadd)
        session.commit()
        session.refresh(toadd)
        return toadd
    else:
        raise HTTPException(status_code=409, detail="email already exists")

