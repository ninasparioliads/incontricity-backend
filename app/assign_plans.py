import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Ad, User
import random

DATABASE_URL = "postgresql://postgres.drehyeczjmwspnvodwol:fmDlrFKOqa2vDGty@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def assign_plans():
    db = SessionLocal()
    
    # Conta annunci totali
    total = db.query(Ad).count()
    print(f"Totale annunci: {total}")
    
    # Calcola quanti VIP e Premium (circa 5% e 10%)
    vip_count = int(total * 0.05)
    premium_count = int(total * 0.10)
    
    print(f"Assegno {vip_count} VIP e {premium_count} Premium...")
    
    # Prendi tutti gli annunci fake (user_id=NULL)
    fake_ads = db.query(Ad).filter(Ad.user_id == None).all()
    print(f"Annunci fake da aggiornare: {len(fake_ads)}")
    
    # Mescola casualmente
    random.shuffle(fake_ads)
    
    # Assegna VIP ai primi N
    for i, ad in enumerate(fake_ads[:vip_count]):
        ad.ad_plan = "vip"
    
    # Assegna Premium ai successivi N
    for i, ad in enumerate(fake_ads[vip_count:vip_count+premium_count]):
        ad.ad_plan = "premium"
    
    # Il resto rimane standard/free
    for i, ad in enumerate(fake_ads[vip_count+premium_count:]):
        ad.ad_plan = "standard"
    
    db.commit()
    print("✓ Piani assegnati con successo!")
    
    # Verifica
    vip = db.query(Ad).filter(Ad.ad_plan == "vip").count()
    premium = db.query(Ad).filter(Ad.ad_plan == "premium").count()
    standard = db.query(Ad).filter(Ad.ad_plan == "standard").count()
    
    print(f"\nRiepilogo:")
    print(f"  VIP: {vip}")
    print(f"  Premium: {premium}")
    print(f"  Standard: {standard}")
    
    db.close()

if __name__ == "__main__":
    assign_plans()
