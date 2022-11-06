import sqlalchemy as db
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String
from dotenv import load_dotenv
import os

Base = declarative_base()


load_dotenv()

engine = db.create_engine(os.getenv("DB_URL"), echo=True)

Session = sessionmaker(bind=engine)
session = Session()


class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    url = Column(String(255))
    category = Column(String(255)) # no leading or trailing slash


    def __repr__(self):
        return f"<Page(name={self.name}, url={self.url}, category={self.category})>"


Base.metadata.create_all(engine)
# Base.metadata.drop_all(engine)


