from models.user import User

class UserRepository:
    def __init__(self,db):
        self.db=db


    def add_user(self,user:User):
        self.db.add(user)
        self.db.commit()

    def save(self, user: User):
        self.db.merge(user)  # ← merge updates existing record
        self.db.commit()

    def get_user_by_email(self,email:str):

        user_data=self.db.query(User).filter(User.email==email).first()
        
        return user_data