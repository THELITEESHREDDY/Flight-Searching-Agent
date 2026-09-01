from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.settings import settings


base = declarative_base()
engine = create_engine(settings.SQLLITE)

Localsession = sessionmaker(bind=engine)


def get_db():
    session = Localsession()
    try:
        
        yield session
    finally:
        session.close()

