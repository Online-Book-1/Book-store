# repositories/book_repository.py
from typing import Dict
from models.book import Book
from models.chapter import Chapter
from models.page import Page

class BookRepository:
    def __init__(self, db):
        self.db = db

    def add_book(self, book: Book):
        self.db.add(book)
        self.db.commit()

    def get_book_by_id(self, book_id: int) -> Book:
        return self.db.query(Book).filter(Book.book_id == book_id).first()

    def get_book_by_user_id(self, user_id: int):
        return self.db.query(Book).filter(Book.author_id == user_id).all()

    def save_chapter(self, chapter: Chapter):
        self.db.add(chapter)
        self.db.commit()
        self.db.refresh(chapter)  # ← now it works because ID is integer
        return chapter
    def save_page(self, page: Page):
        self.db.add(page)
        self.db.commit()

    def get_all_books(self):
       return self.db.query(Book).all()