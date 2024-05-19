from typing import List

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True)
    message_id = Column(String, unique=True, nullable=False)
    from_addr = Column(String, nullable=False)
    to_addr = Column(String, nullable=False)
    subject = Column(String)
    message = Column(String)
    date = Column(DateTime)


def get_db_engine(db_url: str = "sqlite:///emails.db") -> Engine:
    """
    db helper function to create database engine instance.
    :param db_url:
    :return:
    """
    return create_engine(db_url)


def create_tables(engine: Engine):
    """
    function to create tables in db.
    :param engine:
    :return:
    """
    Base.metadata.create_all(engine)


def get_session(engine):
    """
    function to create db session.
    :param engine:
    :return:
    """
    session = sessionmaker(bind=engine)
    return session()


def get_all_records(session) -> List[Email]:
    """
    function to fetch all records of Email table.
    :param session:
    :return:
    """
    return session.query(Email).all()
