# db.py

from sqlalchemy.orm import sessionmaker
from clases import engine

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_session():
    return SessionLocal()
