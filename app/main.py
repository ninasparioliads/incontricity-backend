from fastapi import FastAPI,Query,Depends,HTTPException,Request,BackgroundTasks,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import or_,func
from pydantic import BaseModel,EmailStr
from typing import Optional,List
from datetime import datetime
import math,json
from .database import engine,Base,get_db
from .models import Ad,User,Payment
from .auth import hash_pw,verify_pw,make_token,read_token
from .seed import seed
try:
    from .storage import upload_photos_list, upload_base64
    STORAGE_OK=True
except:
    STORAGE_OK=False
try:
    from .storage import upload_photos_list, upload_base64
    STORAGE_OK=True
except:
    STORAGE_OK=False

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(bind=engine)
    db=next(get_db())
    if db.query(Ad).count()==0: seed(db)
    db.close()
    yield

app=FastAPI(title="IncontriCity API",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*","ngrok-skip-browser-warning"])
oauth2=OAuth2PasswordBearer(tokenUrl="/auth/login",auto_error=False)

def cur_user(token:str=Depends(oauth2),db:Session=Depends(get_db)):
    if not token: return None
    p=read_token(token)
    if not p: return None
    return db.query(User).filter(User.email==p.get("sub")).first()

# ── Schemas ───────────────────────────────────────────────────
class AdOut(BaseModel):
    id:int;name:str;age:int;city:str;country:str;flag:str
    cat:str;lang:str;desc:str;services:str;target:str
    location:str;time:str;verified:bool
    photos:Optional[str]=None; video:Optional[str]=None
    user_id:Optional[int]=None
    services_included:Optional[str]=None; services_extra:Optional[str]=None
    height:Optional[str]=None; weight:Optional[str]=None
    ethnicity:Optional[str]=None; orientation:Optional[str]=None
    eyes:Optional[str]=None; hair_color:Optional[str]=None; hair_length:Optional[str]=None
    smoker:Optional[str]=None; tattoo:Optional[str]=None; piercing:Optional[str]=None
    nationality:Optional[str]=None; languages_spoken:Optional[str]=None
    available_for:Optional[str]=None; meeting_with:Optional[str]=None
    phone:Optional[str]=None; whatsapp:Optional[bool]=None; telegram:Optional[bool]=None
    agency:Optional[str]=None
    rates:Optional[str]=None
    contact_email:Optional[str]=None
    telegram_user:Optional[str]=None
    ad_plan:Optional[str]=None
    paid:Optional[bool]=None
    model_config={"from_attributes":True}

class Page(BaseModel):
    items:List[AdOut];total:int;page:int;pages:int

class UserOut(BaseModel):
    id:int;name:str;email:str;is_admin:bool;plan:str
    avatar:Optional[str]=None
    model_config={"from_attributes":True}

class Token(BaseModel):
    access_token:str;token_type:str="bearer";user:UserOut

class UserCreate(BaseModel):
    name:str;email:EmailStr;password:str

class UserUpdate(BaseModel):
    name:Optional[str]=None
    plan:Optional[str]=None
    avatar:Optional[str]=None   # base64 data URL, already resized client-side

class AdCreate(BaseModel):
    name:str;age:int;city:str;country:str="IT";flag:str=""
    cat:str;lang:str="it";desc:str;services:str=""
    target:str="Tutti";location:str="Online"
    time:str="Pubblicato di recente";verified:bool=False
    photos:Optional[str]=None
    video:Optional[str]=None
    services_included:Optional[str]=None
    services_extra:Optional[str]=None
    height:Optional[str]=None; weight:Optional[str]=None
    ethnicity:Optional[str]=None; orientation:Optional[str]=None
    eyes:Optional[str]=None; hair_color:Optional[str]=None; hair_length:Optional[str]=None
    smoker:Optional[str]=None; tattoo:Optional[str]=None; piercing:Optional[str]=None
    nationality:Optional[str]=None; languages_spoken:Optional[str]=None
    available_for:Optional[str]=None; meeting_with:Optional[str]=None
    phone:Optional[str]=None; whatsapp:Optional[bool]=False; telegram:Optional[bool]=False
    agency:Optional[str]=None
    rates:Optional[str]=None
    contact_email:Optional[str]=None
    telegram_user:Optional[str]=None
    ad_plan:Optional[str]=None
    slot_id:Optional[int]=None

class PaymentCreate(BaseModel):
    amount:str;method:str;plan:str;status:str="completed"

class PaymentOut(BaseModel):
    id:int;user_email:str;amount:str;method:str;plan:str;status:str;date:str
    model_config={"from_attributes":True}


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GMAIL_USER="ninasparioliads@gmail.com"
GMAIL_PASS="nxms ivxh mszh nqjx"

def send_email(to_addr,subject,body):
    try:
        msg=MIMEMultipart()
        msg["From"]=GMAIL_USER
        msg["To"]=to_addr
        msg["Subject"]=subject
        msg.attach(MIMEText(body,"html"))
        with smtplib.SMTP_SSL("smtp.gmail.com",465) as s:
            s.login(GMAIL_USER,GMAIL_PASS)
            s.sendmail(GMAIL_USER,to_addr,msg.as_string())
        return True
    except Exception as e:
        print("Email error:",e)
        return False

# ── ADS ───────────────────────────────────────────────────────
@app.get("/ads",response_model=Page)
def list_ads(cat:Optional[str]=None,country:Optional[str]=None,lang:Optional[str]=None,
             q:Optional[str]=None,page:int=Query(1,ge=1),per_page:int=Query(30,ge=1,le=100),
             user_id:Optional[int]=None,db:Session=Depends(get_db)):
    qr=db.query(Ad).filter((Ad.paid==True)|(Ad.user_id==None))
    if cat: qr=qr.filter(Ad.cat==cat)
    if country: qr=qr.filter(Ad.country==country)
    if lang: qr=qr.filter(Ad.lang==lang)
    if q: qr=qr.filter(or_(Ad.name.ilike(f"%{q}%"),Ad.desc.ilike(f"%{q}%"),Ad.city.ilike(f"%{q}%")))
    if user_id: qr=qr.filter(Ad.user_id==user_id)
    total=qr.count(); items=qr.offset((page-1)*per_page).limit(per_page).all()
    return Page(items=items,total=total,page=page,pages=max(1,math.ceil(total/per_page)))

@app.get("/ads/{ad_id}",response_model=AdOut)
def get_ad(ad_id:int,db:Session=Depends(get_db)):
    ad=db.query(Ad).filter(Ad.id==ad_id).first()
    if not ad: raise HTTPException(404)
    return ad

@app.post("/ads",response_model=AdOut,status_code=201)
def create_ad(body:AdCreate,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    data=body.model_dump()
    if STORAGE_OK:
        if data.get("photos"): data["photos"]=upload_photos_list(data["photos"])
        if data.get("video") and data["video"].startswith("data:"): data["video"]=upload_base64(data["video"],"videos")
    ad=Ad(**data,user_id=user.id)
    db.add(ad); db.commit(); db.refresh(ad)
    # Remove 1 fake ad from same country
    fake=db.query(Ad).filter(Ad.user_id==None, Ad.country==data.get("country","IT")).order_by(Ad.id).first()
    if fake: db.delete(fake); db.commit()
    return ad

@app.put("/ads/{ad_id}",response_model=AdOut)
def update_ad(ad_id:int,body:AdCreate,user=Depends(cur_user),db:Session=Depends(get_db)):
    ad=db.query(Ad).filter(Ad.id==ad_id).first()
    if not ad: raise HTTPException(404)
    if not user or(ad.user_id!=user.id and not user.is_admin): raise HTTPException(403)
    for k,v in body.model_dump().items(): setattr(ad,k,v)
    db.commit(); db.refresh(ad); return ad

@app.delete("/ads/{ad_id}",status_code=204)
def delete_ad(ad_id:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    ad=db.query(Ad).filter(Ad.id==ad_id).first()
    if not ad: raise HTTPException(404)
    if not user or(ad.user_id!=user.id and not user.is_admin): raise HTTPException(403)
    db.delete(ad); db.commit()

# ── AUTH ──────────────────────────────────────────────────────
@app.post("/auth/register",response_model=UserOut,status_code=201)
def register(body:UserCreate,db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==body.email).first():
        raise HTTPException(400,"Email già registrata")
    u=User(name=body.name,email=body.email,hashed_password=hash_pw(body.password))
    db.add(u); db.commit(); db.refresh(u)

    return u

@app.post("/auth/login",response_model=Token)
def login(form:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==form.username).first()
    if not u or not verify_pw(form.password,u.hashed_password):
        raise HTTPException(401,"Credenziali errate")
    return Token(access_token=make_token({"sub":u.email}),user=UserOut.model_validate(u))

@app.get("/auth/me",response_model=UserOut)
def me(user=Depends(cur_user)):
    if not user: raise HTTPException(401)
    return user

@app.put("/auth/me",response_model=UserOut)
def update_me(body:UserUpdate,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    if body.name: user.name=body.name
    if body.plan: user.plan=body.plan
    if body.avatar is not None:
        if STORAGE_OK and body.avatar and body.avatar.startswith("data:"):
            user.avatar=upload_base64(body.avatar,"avatars")
        else:
            user.avatar=body.avatar
    db.commit(); db.refresh(user); return user

# ── PAYMENTS ──────────────────────────────────────────────────
@app.get("/payments/me",response_model=List[PaymentOut])
def my_payments(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    return db.query(Payment).filter(Payment.user_id==user.id).order_by(Payment.id.desc()).all()

@app.post("/payments",response_model=PaymentOut,status_code=201)
def create_payment(body:PaymentCreate,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    p=Payment(user_id=user.id,user_email=user.email,**body.model_dump(),
              date=datetime.now().strftime("%d/%m/%Y %H:%M"))
    db.add(p); db.commit(); db.refresh(p)
    user.plan=body.plan.lower(); db.commit()
    return p

@app.get("/payments",response_model=List[PaymentOut])
def all_payments(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    return db.query(Payment).order_by(Payment.id.desc()).all()

# ── PAYMENTS PLANS ──
@app.get("/ads/pending_payment")
def pending_payment(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    ads=db.query(Ad).filter(Ad.user_id==user.id,Ad.paid==False).all()
    return [{"id":a.id,"name":a.name,"city":a.city,"cat":a.cat,"ad_plan":a.ad_plan,"created":a.time} for a in ads]

@app.post("/ads/{ad_id}/activate")
def activate_ad(ad_id:int,plan:str="free",user=Depends(cur_user),db:Session=Depends(get_db)):
    ad=db.query(Ad).filter(Ad.id==ad_id).first()
    if not ad: raise HTTPException(404)
    if not user or(ad.user_id!=user.id and not user.is_admin): raise HTTPException(403)
    from datetime import datetime,timedelta
    ad.paid=True
    ad.is_active=True
    ad.ad_plan=plan
    if plan=="free":
        ad.expires_at=(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d")
    else:
        ad.expires_at=(datetime.now()+timedelta(days=30)).strftime("%Y-%m-%d")
    db.commit()
    return {"status":"activated","plan":plan,"expires_at":ad.expires_at}

@app.get("/payments/plans")
def get_plans():
    return [
        {"id":"free","name":"Free","price":0,"currency":"EUR","duration_days":30,"description":"1 ad · Standard grid · Expires in 30 days"},
        {"id":"standard","name":"Standard","price":10,"currency":"EUR","duration_days":30,"description":"Standard grid · 30 days visibility"},
        {"id":"premium","name":"Premium","price":40,"currency":"EUR","duration_days":30,"description":"Premium section · 30 days · Priority placement"},
        {"id":"vip","name":"VIP","price":100,"currency":"EUR","duration_days":30,"description":"Featured top · Gold border · Maximum visibility"},
    ]


@app.get("/grid-types")
def get_grid_types():
    return {"types":[
        {"id":1,"name":"vip","label":"⭐ VIP","rows":3,"cols":5,"slides":2,"color":"#d4af37","icon":"⭐","default_price":100.0},
        {"id":2,"name":"premium","label":"💎 Premium","rows":5,"cols":5,"slides":3,"color":"#818cf8","icon":"💎","default_price":40.0}
    ]}

@app.get("/grid-slots")
def get_grid_slots(slot_type:Optional[str]=None,db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    q="SELECT id,slot_type,slide_index,row_index,col_index,price,is_occupied,ad_id FROM grid_slots"
    if slot_type: q+=f" WHERE slot_type='{slot_type}'"
    q+=" ORDER BY slide_index,row_index,col_index"
    rows=db.execute(sqlt(q)).fetchall()
    return{"slots":[{"id":r[0],"type":r[1],"slide":r[2],"row":r[3],"col":r[4],"price":float(r[5]),"is_occupied":r[6],"ad_id":r[7]} for r in rows]}

@app.put("/grid-slots/{slot_id}/price")
def update_slot_price(slot_id:int,price:float,user=Depends(cur_user),db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    if not user or not user.is_admin: raise HTTPException(403)
    db.execute(sqlt(f"UPDATE grid_slots SET price={price} WHERE id={slot_id}"))
    db.commit()
    return{"ok":True}

@app.put("/grid-slots/{slot_id}/occupy")
def occupy_slot(slot_id:int,ad_id:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    if not user: raise HTTPException(401)
    db.execute(sqlt(f"UPDATE grid_slots SET is_occupied=TRUE,ad_id={ad_id} WHERE id={slot_id}"))
    db.commit()
    return{"ok":True}


@app.get("/duration-prices")
def get_duration_prices():
    return {"prices":{
        "standard":[10,50,80,200,400,800],
        "premium":[40,200,320,800,1600,3200],
        "vip":[100,500,800,2000,4000,8000]
    }}

@app.put("/duration-prices/{plan_type}")
def update_duration_prices(plan_type:str,prices:list,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt
    for i,price in enumerate(prices):
        days=[3,7,30,90,180,365][i]
        db.execute(sqlt(f"INSERT INTO duration_prices (plan_type,days,label,price) VALUES ('{plan_type}',{days},'{days}d',{price}) ON CONFLICT (plan_type,days) DO UPDATE SET price={price}"))
    db.commit()
    return{"ok":True}


@app.get("/duration-prices/config")
def get_dur_config(db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    rows=db.execute(sqlt("SELECT key,value FROM config WHERE key IN ('vip_pct','prem_pct','standard_prices')")).fetchall()
    result={"vip_pct":[5,15,30,100,270,510,960],"prem_pct":[4,12,25,100,260,490,920],"standard":[5,10,50,80,200,400,800]}
    for r in rows:
        import json
        result[r[0]]=json.loads(r[1])
    return result

@app.put("/duration-prices/config")
def set_dur_config(data:dict,user=Depends(cur_user),db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    import json
    if not user or not user.is_admin: raise HTTPException(403)
    db.execute(sqlt("CREATE TABLE IF NOT EXISTS config (key VARCHAR(50) PRIMARY KEY, value TEXT)"))
    for k,v in data.items():
        db.execute(sqlt(f"INSERT INTO config (key,value) VALUES ('{k}','{json.dumps(v)}') ON CONFLICT (key) DO UPDATE SET value='{json.dumps(v)}'"))
    db.commit()
    return{"ok":True}


@app.post("/ads/{ad_id}/view")
def track_view(ad_id:int,request:Request,db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    import hashlib
    ip=request.client.host
    today=str(__import__("datetime").date.today())
    key=hashlib.md5(f"{ad_id}:{ip}:{today}".encode()).hexdigest()
    existing=db.execute(sqlt(f"SELECT 1 FROM ad_views WHERE view_key=\'{key}\'")).fetchone()
    if not existing:
        db.execute(sqlt("CREATE TABLE IF NOT EXISTS ad_views (id SERIAL PRIMARY KEY, ad_id INTEGER, view_key VARCHAR(50) UNIQUE, created_at TIMESTAMP DEFAULT NOW())"))
        db.execute(sqlt(f"INSERT INTO ad_views (ad_id,view_key) VALUES ({ad_id},\'{key}\') ON CONFLICT DO NOTHING"))
        db.commit()
    count=db.execute(sqlt(f"SELECT COUNT(*) FROM ad_views WHERE ad_id={ad_id}")).fetchone()[0]
    return{{"count":count,"new":not existing}}

@app.get("/ads/{ad_id}/views")
def get_views(ad_id:int,db:Session=Depends(get_db)):
    from sqlalchemy import text as sqlt
    try:
        count=db.execute(sqlt(f"SELECT COUNT(*) FROM ad_views WHERE ad_id={ad_id}")).fetchone()[0]
        return{{"count":count}}
    except:
        return{{"count":0}}



@app.get("/favorites")
def get_favorites(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    from sqlalchemy import text as sqlt
    rows=db.execute(sqlt(f"SELECT ad_id FROM favorites WHERE user_id={user.id}")).fetchall()
    ad_ids=[r[0] for r in rows]
    if not ad_ids: return []
    ads=db.query(Ad).filter(Ad.id.in_(ad_ids)).all()
    return ads

@app.post("/favorites/{ad_id}")
def add_favorite(ad_id:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    from sqlalchemy import text as sqlt
    db.execute(sqlt(f"INSERT INTO favorites (user_id,ad_id) VALUES ({user.id},{ad_id}) ON CONFLICT DO NOTHING"))
    db.commit()
    return{"ok":True}

@app.delete("/favorites/{ad_id}")
def remove_favorite(ad_id:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    from sqlalchemy import text as sqlt
    db.execute(sqlt(f"DELETE FROM favorites WHERE user_id={user.id} AND ad_id={ad_id}"))
    db.commit()
    return{"ok":True}

@app.get("/favorites/check/{ad_id}")
def check_favorite(ad_id:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: return{"saved":False}
    from sqlalchemy import text as sqlt
    r=db.execute(sqlt(f"SELECT 1 FROM favorites WHERE user_id={user.id} AND ad_id={ad_id}")).fetchone()
    return{"saved":bool(r)}


@app.post("/ads/{ad_id}/request-verification")
def request_verification(ad_id:int,body:dict,background_tasks:BackgroundTasks,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user: raise HTTPException(401)
    ad=db.query(Ad).filter(Ad.id==ad_id).first()
    if not ad: raise HTTPException(404)
    if ad.user_id!=user.id: raise HTTPException(403)

    def _send():
        try:
            subject=f"IncontriCity - Verification request for ad #{ad_id}"
            id_doc=body.get("id_document","")
            selfie=body.get("selfie_document","")
            email_body=f"""
            <h2>Verification Request</h2>
            <p><b>Ad:</b> {ad.name}, {ad.age} - {ad.city}</p>
            <p><b>User:</b> {user.email}</p>
            <p><b>Ad ID:</b> {ad_id}</p>
            <p>ID document attached as base64 image data ({len(id_doc)} chars).</p>
            <p>Selfie attached as base64 image data ({len(selfie)} chars).</p>
            <p>Documents stored - check admin panel or database for full images.</p>
            """
            send_email(GMAIL_USER,subject,email_body)
        except Exception as e:
            print("Verification email failed:",e)

    background_tasks.add_task(_send)

    # Save documents to DB for admin review
    from sqlalchemy import text as sqlt
    import json as _json
    db.execute(sqlt("CREATE TABLE IF NOT EXISTS verification_requests (id SERIAL PRIMARY KEY, ad_id INTEGER, id_document TEXT, selfie_document TEXT, created_at TIMESTAMP DEFAULT NOW())"))
    db.execute(sqlt(f"INSERT INTO verification_requests (ad_id,id_document,selfie_document) VALUES ({ad_id},:idd,:slf)"),
               {"idd":body.get("id_document",""),"slf":body.get("selfie_document","")})
    db.commit()

    return{"ok":True}

@app.put("/ads/{ad_id}/verify")
def set_verified(ad_id:int,verified:bool=True,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    ad=db.query(Ad).filter(Ad.id==ad_id).first()
    if not ad: raise HTTPException(404)
    ad.verified=verified
    db.commit()
    return{"ok":True,"verified":verified}


@app.get("/admin/all-ads")
def admin_all_ads(page:int=Query(1,ge=1),per_page:int=Query(25,ge=1,le=100),
                   user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    total=db.query(Ad).count()
    items=db.query(Ad).order_by(Ad.id.desc()).offset((page-1)*per_page).limit(per_page).all()
    pages=(total+per_page-1)//per_page
    return{"items":items,"total":total,"page":page,"pages":pages}


@app.get("/admin/verifications")
def admin_verifications(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt
    db.execute(sqlt("CREATE TABLE IF NOT EXISTS verification_requests (id SERIAL PRIMARY KEY, ad_id INTEGER, id_document TEXT, selfie_document TEXT, created_at TIMESTAMP DEFAULT NOW(), status VARCHAR(20) DEFAULT 'pending')"))
    rows=db.execute(sqlt("""
        SELECT v.id,v.ad_id,v.id_document,v.selfie_document,v.created_at,v.status,a.name,a.city,a.flag
        FROM verification_requests v
        LEFT JOIN ads a ON a.id=v.ad_id
        ORDER BY v.created_at DESC
    """)).fetchall()
    return[{"id":r[0],"ad_id":r[1],"id_document":r[2],"selfie_document":r[3],
            "created_at":str(r[4]),"status":r[5],"ad_name":r[6],"ad_city":r[7],"ad_flag":r[8]} for r in rows]

@app.put("/admin/verifications/{vid}/approve")
def approve_verification(vid:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt
    row=db.execute(sqlt(f"SELECT ad_id FROM verification_requests WHERE id={vid}")).fetchone()
    if not row: raise HTTPException(404)
    ad=db.query(Ad).filter(Ad.id==row[0]).first()
    if ad: ad.verified=True
    db.execute(sqlt(f"UPDATE verification_requests SET status='approved' WHERE id={vid}"))
    db.commit()
    return{"ok":True}

@app.put("/admin/verifications/{vid}/reject")
def reject_verification(vid:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt
    db.execute(sqlt(f"UPDATE verification_requests SET status='rejected' WHERE id={vid}"))
    db.commit()
    return{"ok":True}


@app.delete("/admin/verifications/{vid}")
def delete_verification(vid:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt
    db.execute(sqlt(f"DELETE FROM verification_requests WHERE id={vid}"))
    db.commit()
    return{"ok":True}


@app.put("/admin/verifications/{vid}/revoke")
def revoke_verification(vid:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt
    row=db.execute(sqlt(f"SELECT ad_id FROM verification_requests WHERE id={vid}")).fetchone()
    if not row: raise HTTPException(404)
    ad=db.query(Ad).filter(Ad.id==row[0]).first()
    if ad: ad.verified=False
    db.execute(sqlt(f"UPDATE verification_requests SET status='rejected' WHERE id={vid}"))
    db.commit()
    return{"ok":True}

# ── ADMIN ─────────────────────────────────────────────────────

@app.get("/admin/pending")
def admin_pending(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    ads=db.query(Ad).filter(Ad.paid==False,Ad.user_id!=None).all()
    result=[]
    for ad in ads:
        u=db.query(User).filter(User.id==ad.user_id).first()
        d=ad.__dict__.copy();d.pop("_sa_instance_state",None)
        d["user_email"]=u.email if u else None
        result.append(d)
    return result

@app.get("/admin/stats")
def stats(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    from sqlalchemy import text as sqlt3
    pays=db.execute(sqlt3("SELECT * FROM payments WHERE status='completed'")).fetchall()
    rev=sum(float(p.amount.replace("€","")) for p in pays)
    total=db.query(Ad).count()
    fake=db.query(Ad).filter(Ad.user_id==None).count()
    return {"total_ads":total,"real_ads":total-fake,"fake_ads":fake,
            "total_users":db.query(User).count(),
            "total_payments":len(pays),"total_revenue":f"€{rev:.2f}"}

@app.get("/admin/users",response_model=List[UserOut])
def admin_users(user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    return db.query(User).all()

@app.delete("/admin/users/{uid}",status_code=204)
def delete_user(uid:int,user=Depends(cur_user),db:Session=Depends(get_db)):
    if not user or not user.is_admin: raise HTTPException(403)
    u=db.query(User).filter(User.id==uid).first()
    if not u: raise HTTPException(404)
    db.delete(u); db.commit()
