# routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from schemas.book import BookCreateSchema,ChapterCreateSchema
from database import get_db
from services.book_manager import BookManager
from services.pagination_services import PaginationService
from services.reader_manager import ReaderManager
from repositories.book_repository import BookRepository
from repositories.progress_repository import ProgressRepository
from utils.jwt import get_curr_user
from datetime import datetime

router = APIRouter()

def get_book_manager(db = Depends(get_db)) -> BookManager:
    book_repo          = BookRepository(db)
    pagination_service = PaginationService()  # ← no db needed
    return BookManager(book_repo, pagination_service)

def get_reader_manager(db = Depends(get_db)) -> ReaderManager:
    progress_repo = ProgressRepository(db)
    book_repo     = BookRepository(db)  # ← create it first!
    return ReaderManager(progress_repo, book_repo)
 
 

@router.post("/book/create_book")
def create_book(book_data: BookCreateSchema, book_manager: BookManager = Depends(get_book_manager),current_user = Depends(get_curr_user)):
    try:
        book = book_manager.add_book(book_title=book_data.book_title, author_id=current_user.user_id)
        return book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/book/create_chapter")
def create_chapter(chapter_data: ChapterCreateSchema, book_manager: BookManager = Depends(get_book_manager),current_user = Depends(get_curr_user)):
    try:
        chapter_id = f"CH_{datetime.now().timestamp()}"
        chapter = book_manager.add_chapter(
    book_id=chapter_data.book_id,
    chapter_id=chapter_id,
    chapter_name=chapter_data.chapter_name,
    text=chapter_data.content
)
        return chapter
    except LookupError as e:
        raise HTTPException(status_code=200, detail=str(e))
    
@router.get("/book/read")
def continue_reading(book_id:int,reader_manager: ReaderManager = Depends(get_reader_manager),current_user = Depends(get_curr_user)):
    try:
         
        text= reader_manager.get_current_page(book_id=book_id,user_id=current_user.user_id)
     
        return text
    # ✅ Correct
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
     

@router.get("/book/readnext")
def read_next(book_id:int,reader_manager: ReaderManager = Depends(get_reader_manager),current_user = Depends(get_curr_user)):
    try:
         
        text= reader_manager.move_next(book_id=book_id,user_id=current_user.user_id)
     
        return text
    # ✅ Correct
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
     

@router.get("/book/getbooks")
def get_your_books(book_manager: BookManager = Depends(get_book_manager),current_user = Depends(get_curr_user)):
    try:
         
        text= book_manager.get_books(user_id=current_user.user_id)
     
        return text
    except LookupError as e:
        raise HTTPException(status_code=200, detail=str(e))
    

@router.get("/book/getrecommendation")
def get_your_books(book_manager: BookManager = Depends(get_book_manager),current_user = Depends(get_curr_user)):
    try:
         
        text= book_manager.get_recommended_books()
     
        return text
    except LookupError as e:
        raise HTTPException(status_code=200, detail=str(e))