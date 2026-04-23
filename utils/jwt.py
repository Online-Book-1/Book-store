
from config import settings
from datetime import datetime,timedelta, timezone
from jose import jwt,JWTError
from schemas.token import TokenData
from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from models.user import User
from database import get_db

oauth2scheme=OAuth2PasswordBearer(tokenUrl='/login')



def create_token_data(token_data: TokenData):
    data = token_data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    data["exp"] = expire
    
    encoded_jwt = jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(token_data: TokenData):
    data = token_data.model_dump()
    expire = datetime.now(timezone.utc) + timedelta(days=7)  # ← 7 days
    data["exp"] = expire
    

# refresh token payload  
    data["type"] = "refresh"
    encoded_jwt = jwt.encode(data, settings.REFRESH_TOKEN_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_refresh_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.REFRESH_TOKEN_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise PermissionError("Refresh token expired. Please login again.")
    except jwt.JWTError:
        raise PermissionError("Invalid refresh token")

def verify_token(token: str, credentials_exception):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("email")  # or whatever field you stored
         
        
        if email is None:
            raise credentials_exception
        
        token_data = TokenData(email=email)
        return token_data
    
    except JWTError:
        raise credentials_exception


def get_curr_user(encoded_tok:str=Depends(oauth2scheme),db:Session=Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data=verify_token(encoded_tok,credentials_exception)

    user=db.query(User).filter(User.email==token_data.email).first()
    if user is None:
        raise credentials_exception
    
    return user
