from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from database import db_init, get_session
from models import User, Post,user_post
from sqlmodel import Session, select
from sqlalchemy import func
from pydantic import BaseModel


@asynccontextmanager
async def lifespan(app : FastAPI):
    db_init()
    yield

class UserBase(BaseModel):
    name: str
    email: str
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

class PostCreate(BaseModel):
    title: str
    content: str
    author_id: int

class PostRead(BaseModel):
    id: int
    title: str
    content: str
    class Config:
        orm_mode = True

class UserWithPosts(BaseModel):
    id: int
    name: str
    posts: list[PostRead]
    class Config:
        orm_mode = True

class PostUpdate(BaseModel):
    title: str|None = None
    content: str|None = None
    class Config:
        orm_mode = True

class PostWithLikers(BaseModel):
    title: str
    likers: list[UserBase]
    class Config:
        orm_mode = True
class LikeCount(BaseModel):
    count: int
    class Config:
        orm_mode = True

app = FastAPI(lifespan=lifespan)

@app.get("/")
def home():
    message = "social media app"
    return  message
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

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    to_delete = session.get(User, user_id)
    if to_delete:
        session.delete(to_delete)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="user not found")
    
@app.get("/posts/") #get all the post which is basically the feed
def get_posts(session:Session = Depends(get_session)):
    stmt = select(Post)
    posts = session.exec(stmt).all()
    return posts
@app.post("/posts/", response_model=PostRead)
def post_posts(to_add: PostCreate, session: Session = Depends(get_session)):
    #lets check if the author_id exists
    new_post = session.get(User,to_add.author_id)
    if new_post:
        new_post = Post(title = to_add.title,content=to_add.content,author_id=to_add.author_id)
        session.add(new_post)
        session.commit()
        session.refresh(new_post)
        return new_post
    else:
        raise HTTPException(status_code=404, detail="the user is not found")
    

    
@app.patch("/posts/{post_id}", response_model= PostRead)
def update_post(post_id:int,data:PostUpdate,session:Session = Depends(get_session)):
    found = session.get(Post,post_id)
    if not found:
        raise HTTPException(status_code=404,detail="post not found")
    else:
        updates =  data.model_dump(exclude_unset=True)
        for attribute, value in updates.items():
            setattr(found,attribute,value)
    session.commit()
    session.refresh(found)
    return found

@app.delete("/posts/{post_id}")
def delete_post(post_id: int, session : Session = Depends(get_session)):
    found = session.get(Post,post_id)
    if not found:
        raise HTTPException(status_code=404, detail="post not found")
    else:
        session.delete(found)
        session.commit()
        message = "deleted successfully"
        return message
    
@app.get("/users/{user_id}/posts", response_model= UserWithPosts) #get the posts of one author
def get_author_posts(user_id: int, session: Session = Depends(get_session)):
    found = session.get(User,user_id)
    if found:
        return found
    else:
        raise HTTPException(status_code=404,detail="user not found")
    
@app.post("/users/{user_id}/posts/{post_id}/like")
def like_post(post_id: int, user_id:int, session: Session = Depends(get_session)):
    #ensure that the user and post exist
    foundPost = session.get(Post,post_id)
    foundUser = session.get(User,user_id)
    if not foundPost:
        raise HTTPException(status_code=404, detail="post not found")
    elif not foundUser:
        raise HTTPException(status_code=404, detail="user not found")
    #ensure if the post already liked
    elif foundUser in foundPost.likers:
        raise HTTPException(status_code=409,detail="the post is already like by this user")
    else:
        link = user_post(author_id=user_id,post_id=post_id)
        session.add(link)
        session.commit()
        session.refresh(link)
        message = "liked"
        return message

@app.get("/posts/{post_id}/likers",response_model=PostWithLikers)
def get_post_likers(post_id:int, session:Session = Depends(get_session)):
        #ensure that the user and post exist
    post = session.get(Post,post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post not found")
    else:
        return post
@app.get("/posts/{post_id}/likecount")#,response_model=LikeCount)
def post_likes_count(post_id: int, session: Session = Depends(get_session)):
    found = session.get(Post,post_id)
    if found:
        stmt = select(func.count(user_post.author_id)).where(user_post.post_id == post_id)
        count = session.exec(stmt).first()
        result = int(count)
        return result
    else:
        raise HTTPException(status_code=404,detail="user not found")