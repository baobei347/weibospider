from sqlalchemy import Column, NVARCHAR, Integer, TEXT, DATETIME, BOOLEAN, VARCHAR, FLOAT
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Weibo(Base):
    __tablename__ = 't_weibo'
    sid = Column(Integer, primary_key=True)
    timestamp = Column(TEXT)
    user_url = Column(TEXT)
    user_name = Column(TEXT)
    weibo_url = Column(TEXT)
    content = Column(TEXT)
    forward = Column(Integer)
    comment = Column(Integer)
    like = Column(Integer)
    image = Column(Integer)
    face = Column(Integer)
    face_title = Column(TEXT)
