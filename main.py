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




@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    to_delete = session.get(User, user_id)
    if to_delete:
        session.delete(to_delete)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="user not found")