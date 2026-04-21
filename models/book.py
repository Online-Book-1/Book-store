from typing import List
from models.chapter import Chapter
from sqlalchemy.orm import relationship
 

from sqlalchemy import String,Column,Integer,ForeignKey
from database import Base
 



class Book(Base):
    __tablename__ = "books"

    book_id=Column(Integer,primary_key=True,autoincrement=True)
    book_title=Column(String(100),nullable=False)
    author_id=Column(Integer,ForeignKey("users.user_id"),nullable=False)
    
    chapters = relationship("Chapter", backref="book")
     