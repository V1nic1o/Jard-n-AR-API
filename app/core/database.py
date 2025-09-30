#database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv() # Carga las variables del archivo .env

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Añadimos esta función para que los routers la usen
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()