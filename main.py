from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from database import db_init, get_session
from models import User, Post,user_post
from sqlmodel import Session, select, update
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app : FastAPI):
    db_init()
    yield

class UserBase(BaseModel):
    name: str
    email: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

app = FastAPI(lifespan=lifespan)


#create user

@app.post("/users/")
def add_user(user: UserBase,session: Session = Depends(get_session)):
    found = session.exec(select(User).where(User.email == user.email)).all()
    if found:
        raise HTTPException(status_code=409,detail="Email linked to another user.")
    
    toadd = User(name = user.name, email = user.email)
    session.add(toadd)
    session.commit()
    session.refresh(toadd)
    return toadd

# get users

@app.get("/users/")
def get_users(session : Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users


#update users

@app.patch("/users/{user_id}")
def update_user(user_id : int, data : UserUpdate, session : Session = Depends(get_session)):

    found = session.get(User,user_id)
    if not found:
        raise HTTPException(status_code=404, detail = "User Not Found")

    updates = data.model_dump(exclude_unset=True)   
    for attribute, value in updates.items():
        setattr(found,attribute,value)
    
    session.commit()
    session.refresh(found)
    return found



#delete users