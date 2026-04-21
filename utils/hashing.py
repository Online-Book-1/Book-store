from passlib.context import CryptContext


 

pwd_context=CryptContext(schemes=["argon2"],deprecated='auto')


def get_pass_hash(plain_password):
    return pwd_context.hash(plain_password)

def verify_password(raw_pass,original_pass):
    return pwd_context.verify(raw_pass,original_pass)