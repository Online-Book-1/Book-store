# services/book_manager.py
from repositories.book_repository import BookRepository
from services.pagination_services import PaginationService
from models.book import Book
from models.chapter import Chapter
from datetime import datetime
import random

class BookManager:
    def __init__(self, book_repo: BookRepository, pagination_service: PaginationService):
        self.book_repository    = book_repo
        self.pagination_service = pagination_service

    def add_book(self, book_title: str, author_id: int) -> Book:
        book_id = int(datetime.now().timestamp())
        book = Book(
            book_id    = book_id,
            book_title = book_title,
            author_id  = author_id
        )
        self.book_repository.add_book(book)
        return book

    def add_chapter(self, book_id: int, chapter_name: str, text: str):
        book = self.book_repository.get_book_by_id(book_id)
        if not book:
            raise LookupError("Book not found")

        chapter = Chapter(chapter_name=chapter_name, book_id=book_id)
        saved_chapter = self.book_repository.save_chapter(chapter)

        new_pages = self.pagination_service.create_pages(text)
        for page in new_pages:
            page.chapter_id = saved_chapter.chapter_id
            self.book_repository.save_page(page)

        # ✅ Increment total_chapters count
        book.total_chapters = (book.total_chapters or 0) + 1
        self.book_repository.add_book(book)

        return {"chapter_name": chapter_name, "pages": len(new_pages)}
    
    def get_books(self, user_id: int):
        books = self.book_repository.get_book_by_user_id(user_id)
        if not books:
            raise LookupError("No books found")
        return books
    
    
    def get_book_detail(self,book_id:int):
        book=self.book_repository.get_book_by_id(book_id)
        if not book:
            raise LookupError("No books found")
        return book

        

    def get_recommended_books(self):
        all_books = self.book_repository.get_all_books()
        if not all_books:
            return []
        return random.sample(all_books, min(6, len(all_books)))  # ← return 6 random books