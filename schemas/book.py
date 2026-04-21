# schemas/book.py
from pydantic import BaseModel

class BookCreateSchema(BaseModel):
    book_title: str
      

class ChapterCreateSchema(BaseModel):
    book_id:int
    chapter_name: str
    content:str
      
 
     