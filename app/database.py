import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
DB=os.getenv("DATABASE_URL",f"postgresql://{os.getenv('USER','postgres')}@localhost/incontricity")
engine=create_engine(DB, pool_pre_ping=True)
Session=sessionmaker(bind=engine)
class Base(DeclarativeBase): pass
def get_db():
    db=Session()
    try: yield db
    finally: db.close()
