

 

from sqlalchemy import String,Column,Integer,ForeignKey,TEXT
from database import Base
 



class Page(Base):
    __tablename__ = "pages"

    page_id=Column(Integer,primary_key=True,autoincrement=True)
    page_no=Column(Integer,nullable=False)
     
    content=Column(TEXT,nullable=False)
    chapter_id=Column(Integer,ForeignKey("chapters.chapter_id"),nullable=False)
     