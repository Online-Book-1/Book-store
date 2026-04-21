
from typing import Dict
from models.reading_progress import ReadingProgress

class ProgressRepository:
    def __init__(self,db):
        self.db=db

    def save_progress(self, readingprogress: ReadingProgress):
        self.db.add(readingprogress)
        self.db.commit()

    def get_progress(self, user_id: int, book_id: int) -> ReadingProgress:

        progress=self.db.query(ReadingProgress).filter(ReadingProgress.book_id==book_id, ReadingProgress.user_id==user_id).first()
        if not progress:
            progress = ReadingProgress(user_id=user_id,book_id=book_id)

            self.db.add(progress)
            self.db.commit()
        return progress
         

