 

from sqlalchemy import String,Column,Integer,TIMESTAMP,ForeignKey
from database import Base
from datetime import datetime


class ReadingProgress(Base):
    __tablename__ = "readingprogress"

    reading_id=Column(Integer,primary_key=True,autoincrement=True)
    
    current_chapter_index= Column(Integer,default=0,nullable=False)
    current_page_index= Column(Integer,default=0,nullable=False)
    user_id=Column(Integer,ForeignKey("users.user_id"),nullable=False)               
    book_id=Column(Integer,ForeignKey("books.book_id"),nullable=False)
     