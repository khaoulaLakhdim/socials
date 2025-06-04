from sqlmodel import SQLModel, Field,Relationship
from typing import List

class user_post(SQLModel, table= True):
    author_id: int = Field(foreign_key="user.id", primary_key= True)
    post_id: int = Field(foreign_key="post.id", primary_key= True)

class User(SQLModel, table= True):
    id: int | None = Field(default= None, primary_key=True)
    name: str
    email: str
    posts: List["Post"] = Relationship(back_populates="author")
    likes: List["Post"] = Relationship(back_populates="likers", link_model= user_post)

class Post(SQLModel, table= True):
    id: int | None = Field(default= None, primary_key=True)
    title: str
    content: str
    author_id: int = Field(foreign_key="user.id")
    author: User = Relationship(back_populates= "posts")
    likers: List["User"] = Relationship(back_populates="likes", link_model=user_post)


