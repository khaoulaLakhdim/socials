from sqlmodel import SQLModel, Field


class Test(SQLModel, table = True):
    __tablename__ = "tests"
    id: int|None = Field(default = None, primary_key= True)