import os,bcrypt
from datetime import datetime,timedelta
from jose import jwt,JWTError
SECRET=os.getenv("SECRET_KEY","incontricity-secret-2024!")
ALGO="HS256"
def hash_pw(p): return bcrypt.hashpw(p.encode()[:72],bcrypt.gensalt()).decode()
def verify_pw(plain,hashed): return bcrypt.checkpw(plain.encode()[:72],hashed.encode())
def make_token(data,hours=48):
    return jwt.encode({**data,"exp":datetime.utcnow()+timedelta(hours=hours)},SECRET,ALGO)
def read_token(token):
    try: return jwt.decode(token,SECRET,algorithms=[ALGO])
    except JWTError: return None
