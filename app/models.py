from sqlalchemy import Column,Integer,String,Boolean,Text,ForeignKey,LargeBinary
from .database import Base

class User(Base):
    __tablename__="users"
    id=Column(Integer,primary_key=True)
    name=Column(String(100))
    email=Column(String(200),unique=True,index=True)
    hashed_password=Column(String(200))
    is_admin=Column(Boolean,default=False)
    plan=Column(String(20),default="free")
    avatar=Column(Text, nullable=True)   # base64 data URL

class Ad(Base):
    __tablename__="ads"
    id=Column(Integer,primary_key=True)
    name=Column(String(100)); age=Column(Integer); city=Column(String(100))
    country=Column(String(10)); flag=Column(String(10))
    cat=Column(String(50),index=True); lang=Column(String(10),index=True)
    desc=Column(Text); services=Column(String(500))
    target=Column(String(50)); location=Column(String(100))
    time=Column(String(50)); verified=Column(Boolean,default=False)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=True)
    height=Column(String(20),nullable=True)
    weight=Column(String(20),nullable=True)
    ethnicity=Column(String(50),nullable=True)
    orientation=Column(String(50),nullable=True)
    eyes=Column(String(30),nullable=True)
    hair_color=Column(String(30),nullable=True)
    hair_length=Column(String(30),nullable=True)
    smoker=Column(String(20),nullable=True)
    tattoo=Column(String(10),nullable=True)
    piercing=Column(String(10),nullable=True)
    nationality=Column(String(50),nullable=True)
    languages_spoken=Column(String(100),nullable=True)
    available_for=Column(String(50),nullable=True)
    meeting_with=Column(String(50),nullable=True)
    phone=Column(String(30),nullable=True)
    whatsapp=Column(Boolean,default=False)
    telegram=Column(Boolean,default=False)
    agency=Column(String(100),nullable=True)
    services_included=Column(Text,nullable=True)
    services_extra=Column(Text,nullable=True)
    photos=Column(Text,nullable=True)   # JSON array of base64 data URLs
    video=Column(Text,nullable=True)    # base64 data URL

class Payment(Base):
    __tablename__="payments"
    id=Column(Integer,primary_key=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=True)
    height=Column(String(20),nullable=True)
    weight=Column(String(20),nullable=True)
    ethnicity=Column(String(50),nullable=True)
    orientation=Column(String(50),nullable=True)
    eyes=Column(String(30),nullable=True)
    hair_color=Column(String(30),nullable=True)
    hair_length=Column(String(30),nullable=True)
    smoker=Column(String(20),nullable=True)
    tattoo=Column(String(10),nullable=True)
    piercing=Column(String(10),nullable=True)
    nationality=Column(String(50),nullable=True)
    languages_spoken=Column(String(100),nullable=True)
    available_for=Column(String(50),nullable=True)
    meeting_with=Column(String(50),nullable=True)
    phone=Column(String(30),nullable=True)
    whatsapp=Column(Boolean,default=False)
    telegram=Column(Boolean,default=False)
    agency=Column(String(100),nullable=True)
    services_included=Column(Text,nullable=True)
    services_extra=Column(Text,nullable=True)
    user_email=Column(String(200)); amount=Column(String(20))
    method=Column(String(50)); plan=Column(String(50))
    status=Column(String(20),default="completed"); date=Column(String(50))
