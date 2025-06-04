from sqlmodel import create_engine, Session, SQLModel


DATABASE_URL = "postgresql+psycopg2://postgres:nour123654789@localhost:5433/example"
engine = create_engine(DATABASE_URL, echo= True)

def db_init():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
    
