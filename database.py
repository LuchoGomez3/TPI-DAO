from sqlmodel import SQLModel, create_engine, Session
import os

# Nombre simple, se creará en la misma carpeta del proyecto
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# check_same_thread=False es vital para FastAPI + SQLite
connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session