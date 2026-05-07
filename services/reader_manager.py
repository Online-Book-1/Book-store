
from database import get_db

from repositories.book_repository import BookRepository
from repositories.progress_repository import ProgressRepository


class ReaderManager:
    def __init__(self, progress_repo: ProgressRepository, book_repo: BookRepository):
        self.progress_repository = progress_repo
        self.book_repository     = book_repo

    def get_current_page(self, user_id: int, book_id: int) -> str:
        progress = self.progress_repository.get_progress(user_id, book_id)
        book     = self.book_repository.get_book_by_id(book_id)

        # ✅ Check chapters exist
        if not book.chapters:
            raise LookupError("This book has no chapters yet")

        chapter = book.chapters[progress.current_chapter_index]

        # ✅ Check pages exist
        if not chapter.pages:
            raise LookupError("This chapter has no pages yet")

        page = chapter.pages[progress.current_page_index]
        return f"[{book.book_title} → {chapter.chapter_name} → Page {page.page_no}]\n{page.content}"
    def move_next(self, user_id: int, book_id: int):
        progress = self.progress_repository.get_progress(user_id, book_id)
        book     = self.book_repository.get_book_by_id(book_id)
        
        if not book:
            raise LookupError("Book not found")  # ← case 1
        
        chapter = book.chapters[progress.current_chapter_index]
        if progress.current_page_index < len(chapter.pages) - 1:
            progress.current_page_index += 1
        elif progress.current_chapter_index < len(book.chapters) - 1:
            progress.current_chapter_index += 1
            progress.current_page_index = 0
        else:
            raise LookupError("You have finished the book!")  # ← case 2
        
        self.progress_repository.save_progress(progress)
        return self.get_current_page(user_id, book_id)