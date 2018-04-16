from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey

from fanfic_library import utils

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

    def update_with(self, other_ff):
        self.title = other_ff.title
        self.author = utils.or_else(other_ff.author, self.author)
        self.words = utils.or_else(other_ff.words, self.words)
        self.summary = utils.or_else(other_ff.summary, self.summary)


class Threadmark(Base):
    __tablename__ = 'threadmarks'

    post_id = Column(Integer, primary_key=True)
    fanfic_id = Column(Integer, ForeignKey('fanfics.id'))

    title = Column(String)
    words = Column(Integer)
    likes = Column(Integer)
    author = Column(String)
    published = Column(DateTime)

    def update_with(self, other_tm):
        self.post_id = other_tm.post_id
        self.title = other_tm.title
        self.words = other_tm.words
        self.likes = other_tm.likes
        self.author = other_tm.author
        self.published = other_tm.published

    def __hash__(self):
        return hash((self.post_id, self.title, self.words, self.likes, self.author, self.published))
