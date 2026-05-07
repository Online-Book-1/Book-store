from fastapi import FastAPI
from routes.book_routes import router as book_router
from routes.user_routes import router as user_router

from database import Base, engine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500",   # local dev
                   "http://16.171.40.255"],     # production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)
 
app.include_router(book_router)
app.include_router(user_router)