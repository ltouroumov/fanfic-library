from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean

from fanfic_library import utils

Base = declarative_base()
session = scoped_session(sessionmaker())


class Fanfic(Base):
    __tablename__ = 'fanfics'

    id = Column(Integer, primary_key=True)
    thread_type = Column(String, index=True)
    thread_id = Column(Integer, index=True)
    title = Column(String)
    author = Column(String, nullable=True)
    words = Column(Integer, default=0)
    published = Column(DateTime, nullable=True)
    tags = Column(String, default="")
    language = Column(String, default="Unkown")
    status = Column(String, default="Unkown")
    summary = Column(Text, nullable=True)
    thread_url = Column(String)

    threadmarks = relationship("Threadmark", cascade="all, delete, delete-orphan")

    @property
    def thread_key(self):
        return "%s-%d" % (self.thread_type, self.thread_id)

    def update_with(self, other_ff):
        self.title = other_ff.title
        self.author = utils.or_else(other_ff.author, self.author)
        self.words = utils.or_else(other_ff.words, self.words)
        self.published = utils.or_else(other_ff.published, self.published)
        self.tags = utils.or_else(other_ff.tags, self.tags)
        self.language = utils.or_else(other_ff.language, self.language)
        self.status = utils.or_else(other_ff.status, self.status)
        self.summary = utils.or_else(other_ff.summary, self.summary)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr(self.__dict__)


class Threadmark(Base):
    __tablename__ = 'threadmarks'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, index=True)
    fanfic_id = Column(Integer, ForeignKey('fanfics.id'))

    title = Column(String)
    words = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    author = Column(String, nullable=True)
    published = Column(DateTime, nullable=True)
    local = Column(Boolean, default=False)

    def update_with(self, other_tm):
        self.post_id = other_tm.post_id
        self.title = other_tm.title
        self.words = other_tm.words
        self.likes = other_tm.likes
        self.author = other_tm.author
        self.published = other_tm.published

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr(self.__dict__)

    def __hash__(self):
        return hash((self.post_id, self.title, self.words, self.likes, self.author, self.published))
