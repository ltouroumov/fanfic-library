from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

Base = declarative_base()
session = scoped_session(sessionmaker())


class Fanfic(Base):
    __tablename__ = 'fanfics'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String, nullable=True)
    words = Column(Integer, default=0)
    summary = Column(Text, nullable=True)
    thread_url = Column(String)

    threadmarks = relationship("Threadmark", cascade="all, delete, delete-orphan")


class Threadmark(Base):
    __tablename__ = 'threadmarks'

    post_id = Column(Integer, primary_key=True)
    fanfic_id = Column(Integer, ForeignKey('fanfics.id'))

    title = Column(String)
    words = Column(Integer)
    likes = Column(Integer)
    author = Column(String)
    published = Column(DateTime)
