
from pydantic import BaseModel

class TokenData(BaseModel):
    email:str
   

class Token(BaseModel):
    access_token:str
    token_type:str