from sqlmodel import SQLModel, create_engine, Session

from config import db_url, db_debug
from .models import Media, Reaction, Hashtag, User, Message


engine = create_engine(
        db_url,
        echo=db_debug,
        connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
