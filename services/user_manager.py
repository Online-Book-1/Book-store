# services/user_manager.py
from repositories.user_repository import UserRepository
from models.user import User
from datetime import datetime
from utils.hashing import get_pass_hash,verify_password
from utils.jwt import create_token_data
from schemas.token import TokenData

class UserManager:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def add_user(self, username: str, email: str, password: str) -> User:
        existing_user = self.user_repo.get_user_by_email(email)
        if existing_user:
            raise ValueError("Email already registered")
        
        user_id = int(datetime.now().timestamp())

        hash_passcode=get_pass_hash(password)
        user=User(user_id=user_id, username=username, email=email, password=hash_passcode)  # ← keyword args ✅

         
        self.user_repo.add_user(user)
        return user
    
    def save(self,user:User):
        self.user_repo.save(user)

    def login(self, email: str, password: str) -> User:
        user = self.user_repo.get_user_by_email(email)
        
        if not user:
            raise LookupError("User not found")
        
        if not verify_password(password,user.password):
            raise PermissionError("Invalid credentials")
        
        token_data=create_token_data(TokenData(email=email))
        return {"access_token":token_data,"token_type":"Bearer"}
    
    def get_user_by_email(self, email: str):
        return self.user_repo.get_user_by_email(email)

    def create_verified_user(self, username: str, email: str, hashed_password: str):
        from datetime import datetime
        user_id = int(datetime.now().timestamp())
        user = User(user_id=user_id, username=username, email=email, password=hashed_password)
        self.user_repo.add_user(user)
        return user