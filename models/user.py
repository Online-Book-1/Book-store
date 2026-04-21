from sqlalchemy import String,Column,Integer,TIMESTAMP
from database import Base
from datetime import datetime



class User(Base):
    __tablename__ = "users"

    user_id=Column(Integer,primary_key=True,autoincrement=True)
    username=Column(String(100),nullable=False)
    email=Column(String(100),nullable=False)
    password=Column(String(100),nullable=False)
    created_at=Column(TIMESTAMP,default=datetime.now,nullable=False)