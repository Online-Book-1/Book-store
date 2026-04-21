 


from sqlalchemy import String,Column,Integer,ForeignKey
from database import Base
from sqlalchemy.orm import relationship
 



class Chapter(Base):
    __tablename__ = "chapters"

    chapter_id=Column(Integer,primary_key=True,autoincrement=True)
    chapter_name=Column(String(100),nullable=False)
    book_id=Column(Integer,ForeignKey("books.book_id"),nullable=False)

    pages = relationship("Page", backref="chapter")
     