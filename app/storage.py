import os, uuid, base64, mimetypes, json
from supabase import create_client

SUPA_URL = os.getenv("SUPABASE_URL", "https://drehyeczjmwspnvodwol.supabase.co")
SUPA_KEY = os.getenv("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRyZWh5ZWN6am13c3Budm9kd29sIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODIzNjc4MzEsImV4cCI6MjA5Nzk0MzgzMX0.2QiSf2e_7mS6WFG-Jg-cScXdlREMGGr9RBVSjp5uEgM")
BUCKET = "media"

def get_client():
    return create_client(SUPA_URL, SUPA_KEY)

def upload_base64(data_url: str, folder: str = "photos") -> str:
    if not data_url or not data_url.startswith("data:"):
        return data_url
    try:
        header, b64 = data_url.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
        ext = mimetypes.guess_extension(mime) or ".jpg"
        ext = ext.replace(".jpe", ".jpg")
        file_bytes = base64.b64decode(b64)
        filename = f"{folder}/{uuid.uuid4()}{ext}"
        client = get_client()
        client.storage.from_(BUCKET).upload(
            filename, file_bytes,
            file_options={"content-type": mime, "cache-control": "3600", "upsert": "false"}
        )
        return client.storage.from_(BUCKET).get_public_url(filename)
    except Exception as e:
        print(f"Storage upload error: {e}")
        return data_url

def upload_photos_list(photos_json: str) -> str:
    if not photos_json:
        return photos_json
    try:
        photos = json.loads(photos_json)
        urls = [upload_base64(p, "photos") if p.startswith("data:") else p for p in photos]
        return json.dumps(urls)
    except:
        return photos_json
