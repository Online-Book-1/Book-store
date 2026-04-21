from fastapi import FastAPI
from routes.book_routes import router as book_router
from routes.user_routes import router as user_router

from database import Base, engine

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],        # allow GET, POST, OPTIONS etc.
    allow_headers=["*"],        # allow all headers including Authorization
)

Base.metadata.create_all(bind=engine)
 
app.include_router(book_router)
app.include_router(user_router)