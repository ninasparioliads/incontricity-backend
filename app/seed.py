import json,os,random
from datetime import datetime,timedelta
from .models import Ad,User,Payment
from .auth import hash_pw
SVCS=["pos69","anal","bdsm","bondage","casual_photos","classic_vaginal","couples","cum_face","cum_mouth","cum_body","cunnilingus","deepthroat","dirty_talk","domination","dp_anal","dp_vaginal","duo_girl","erotic_massage","erotic_photos","extraball","facefuck","facesitting","findom","fingering","fisting","foot_fetish","french_kiss","gfe","golden_give","golden_receive","group_sex","handjob","kamasutra","masturbation","oral_no_condom","pse","prostate","rimming_active","rimming_passive","roleplay","sex_breasts","sex_toys","shower","squirting","strapon","striptease","submissive","swallowing","uniforms","video_sex","with_2men","dinner","travel","party","conversation","sport","cinema","art","music","dance","cooking","yoga","photography","shopping","theatre","meditation","trekking","cycling","surf"]
HEIGHTS=["155 cm","160 cm","165 cm","168 cm","170 cm","172 cm","175 cm","178 cm","180 cm","182 cm"]
WEIGHTS=["48 kg","52 kg","55 kg","58 kg","60 kg","63 kg","65 kg","68 kg","70 kg","75 kg"]
ETHNI=["Caucasian","Latin","Asian","African","Middle Eastern","Mixed","Eastern European","Mediterranean"]
ORI={"it":["Eterosessuale","Omosessuale","Bisessuale"],"en":["Heterosexual","Homosexual","Bisexual"],"es":["Heterosexual","Homosexual","Bisexual"],"pt":["Heterossexual","Homossexual","Bissexual"],"fr":["Heterosexuel","Homosexuel","Bisexuel"],"de":["Heterosexuell","Homosexuell","Bisexuell"],"ja":["異性愛","同性愛","両性愛"],"ko":["이성애","동성애","양성애"]}
EYES={"it":["Marroni","Verdi","Azzurri","Neri"],"en":["Brown","Green","Blue","Black"],"es":["Marrones","Verdes","Azules","Negros"],"pt":["Castanhos","Verdes","Azuis","Pretos"],"fr":["Marrons","Verts","Bleus","Noirs"],"de":["Braun","Gruen","Blau","Schwarz"],"ja":["茶色","緑","青","黒"],"ko":["갈색","초록","파란","검정"]}
HAIR={"it":["Bionda","Bruna","Rossa","Nera"],"en":["Blonde","Brunette","Red","Black"],"es":["Rubia","Morena","Pelirroja","Negra"],"pt":["Loura","Morena","Ruiva","Preta"],"fr":["Blonde","Brune","Rousse","Noire"],"de":["Blond","Braun","Rot","Schwarz"],"ja":["ブロンド","ブルネット","赤","黒"],"ko":["금발","갈색","빨간","검정"]}
HAIRLEN={"it":["Corti","Medi","Lunghi"],"en":["Short","Medium","Long"],"es":["Cortos","Medios","Largos"],"pt":["Curtos","Medios","Longos"],"fr":["Courts","Moyens","Longs"],"de":["Kurz","Mittel","Lang"],"ja":["短い","中程度","長い"],"ko":["짧은","중간","긴"]}
SMK={"it":["No","Si","A volte"],"en":["No","Yes","Sometimes"],"es":["No","Si","A veces"],"pt":["Nao","Sim","As vezes"],"fr":["Non","Oui","Parfois"],"de":["Nein","Ja","Manchmal"],"ja":["なし","あり","時々"],"ko":["아니","예","가끔"]}
YN={"it":["No","Si"],"en":["No","Yes"],"es":["No","Si"],"pt":["Nao","Sim"],"fr":["Non","Oui"],"de":["Nein","Ja"],"ja":["なし","あり"],"ko":["아니","예"]}
NATS={"IT":"Italiana","BR":"Brasileira","ES":"Espanola","MX":"Mexicana","CO":"Colombiana","AR":"Argentina","US":"American","UK":"British","DE":"Deutsch","FR":"Francaise","JP":"Japonesa","KR":"Korean","PT":"Portuguesa","AU":"Australian","CA":"Canadian"}
LNGS={"IT":"Italiano, Inglese","BR":"Portugues, Ingles","ES":"Espanol, Ingles","MX":"Espanol","CO":"Espanol","AR":"Espanol","US":"English","UK":"English","DE":"Deutsch, Englisch","FR":"Francais, Anglais","JP":"Giapponese, English","KR":"Coreano, English","PT":"Portugues, Ingles","AU":"English","CA":"English, French"}
AVL={"it":["Outcall","Incall","Outcall + Incall","Online"],"en":["Outcall","Incall","Outcall + Incall","Online"],"es":["Outcall","Incall","Outcall + Incall"],"pt":["Outcall","Incall","Online"],"fr":["Outcall","Incall"],"de":["Outcall","Incall","Online"],"ja":["Outcall","Incall"],"ko":["Outcall","Incall"]}
MTG={"it":["Solo uomini","Solo donne","Entrambi","Tutti"],"en":["Men only","Women only","Both","Everyone"],"es":["Solo hombres","Solo mujeres","Ambos"],"pt":["So homens","So mulheres","Ambos"],"fr":["Hommes","Femmes","Les deux"],"de":["Nur Maenner","Nur Frauen","Beide"],"ja":["男性のみ","女性のみ","両方"],"ko":["남성만","여성만","둘다"]}

def enrich(a,idx):
    lg=a.get("lang","en"); lg=lg if lg in ORI else "en"
    co=a.get("country","US")
    random.seed(idx+hash(a.get("name","")+co))
    n=random.randint(4,14); e=random.randint(0,5)
    s=random.sample(SVCS,min(n+e,len(SVCS)))
    a["services_included"]=json.dumps(s[:n])
    a["services_extra"]=json.dumps(s[n:n+e])
    a["height"]=random.choice(HEIGHTS)
    a["weight"]=random.choice(WEIGHTS)
    a["ethnicity"]=random.choice(ETHNI)
    a["orientation"]=random.choice(ORI.get(lg,ORI["en"]))
    a["eyes"]=random.choice(EYES.get(lg,EYES["en"]))
    a["hair_color"]=random.choice(HAIR.get(lg,HAIR["en"]))
    a["hair_length"]=random.choice(HAIRLEN.get(lg,HAIRLEN["en"]))
    a["smoker"]=random.choice(SMK.get(lg,SMK["en"]))
    a["tattoo"]=random.choice(YN.get(lg,YN["en"]))
    a["piercing"]=random.choice(YN.get(lg,YN["en"]))
    a["nationality"]=NATS.get(co,"International")
    a["languages_spoken"]=LNGS.get(co,"English")
    a["available_for"]=random.choice(AVL.get(lg,AVL["en"]))
    a["meeting_with"]=random.choice(MTG.get(lg,MTG["en"]))
    a["whatsapp"]=random.choice([True,False])
    a["telegram"]=random.choice([True,False])
    return a

def seed(db):
    if db.query(User).count()>0: return
    users=[
        User(name="Admin",email="admin@incontricity.com",hashed_password=hash_pw("admin123"),is_admin=True,plan="vip"),
        User(name="Mario Rossi",email="mario@test.com",hashed_password=hash_pw("test123"),plan="premium"),
        User(name="Laura Bianchi",email="laura@test.com",hashed_password=hash_pw("test123"),plan="free"),
    ]
    db.add_all(users); db.commit()
    jp=os.path.join(os.path.dirname(__file__),"..","ads_data.json")
    ads=[]
    if os.path.exists(jp):
        with open(jp,encoding="utf-8") as f: ads=json.load(f)
        for a in ads:
            if isinstance(a.get("services"),list): a["services"]=",".join(a["services"])
    if not ads:
        ads=[{"name":"Sofia","age":28,"city":"Roma","country":"IT","flag":"🇮🇹","cat":"donna-uomo","lang":"it","desc":"Sono una donna solare.","services":"Compagnia","target":"Uomini","location":"In locale","time":"Pubblicato di recente","verified":True}]
    ads=[enrich(a,i) for i,a in enumerate(ads)]
    COLS={c.key for c in Ad.__table__.columns}
    SK={"id","photos","video"}
    u2=db.query(User).filter(User.email=="mario@test.com").first()
    for a in ads[:2]:
        db.add(Ad(**{k:v for k,v in a.items() if k in COLS and k not in SK},user_id=u2.id if u2 else None))
    batch=[Ad(**{k:v for k,v in a.items() if k in COLS and k not in SK}) for a in ads[2:]]
    for i in range(0,len(batch),500): db.bulk_save_objects(batch[i:i+500]); db.commit()
    db.commit()
    payments=[
        Payment(user_id=2,user_email="mario@test.com",plan="Premium",amount="€9.99",method="Carta di credito",status="completed",date=(datetime.now()-timedelta(days=5)).strftime("%d/%m/%Y %H:%M")),
        Payment(user_id=1,user_email="admin@incontricity.com",plan="VIP",amount="€24.99",method="PayPal",status="completed",date=(datetime.now()-timedelta(days=2)).strftime("%d/%m/%Y %H:%M")),
    ]
    db.add_all(payments); db.commit()
    print(f"Seeded {len(ads)} ads with full profile data")
