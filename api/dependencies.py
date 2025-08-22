from sqlmodel import Session
from database.connection import engine


def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session