import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()


SQLALCHEMY_DATABASE_URL = f'postgresql://{os.getenv("USER")}:{os.getenv("PASSWORD")}@{os.getenv("HOST")}:{os.getenv("PORT")}/todo'


engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Создает и возвращает сессию базы данных.

    Yields:
        Session: Объект сессии базы данных.

    Note:
        Эта функция используется как зависимость в FastAPI для получения сессии базы данных.
        После использования сессия автоматически закрывается.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
