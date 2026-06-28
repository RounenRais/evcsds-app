import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse

from predict_and_ocr import sayac_analiz_et
from key_utils import key_gecerli_mi, key_uret, key_sahibi

# ─── Uygulama ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="EVCSDS Sayaç Analiz API",
    description="Elektrik sayacı fotoğrafından faz tespiti yapar.",
    version="1.0.0"
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ─── Yardımcı Fonksiyon ───────────────────────────────────────────────────────

def api_key_dogrula(api_key: str) -> str:
    """
    Gelen key'i kontrol eder.
    Geçersizse 401 hatası fırlatır, geçerliyse sahibinin adını döner.
    
    Bu fonksiyonu her korumalı endpoint'te çağıracağız.
    """
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key gerekli. Header'a 'X-API-Key' ekleyin."
        )
    if not key_gecerli_mi(api_key):
        raise HTTPException(
            status_code=401,
            detail="Geçersiz API key."
        )
    return key_sahibi(api_key)


# ─── Endpoint'ler ─────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"mesaj": "EVCSDS API çalışıyor", "versiyon": "1.0.0"}


@app.get("/health")
def health():
    return {"durum": "ok"}


@app.post("/keys/generate")
def generate_key(kullanici_adi: str):
    """
    Yeni API key üretir.
    
    Gerçek projede bu endpoint şifreyle korunur,
    şimdilik açık bırakıyoruz test için.
    """
    yeni_key = key_uret(kullanici_adi)
    return {
        "kullanici": kullanici_adi,
        "api_key": yeni_key,
        "mesaj": "Bu key'i güvenli bir yerde saklayın, bir daha gösterilmez."
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)   # Header'dan "X-API-Key" değerini alır
):
    # 1. Key kontrolü
    kullanici = api_key_dogrula(x_api_key)

    # 2. Sadece görsel kabul et
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Sadece görsel dosyası gönderin (jpg, png...)"
        )

    # 3. Geçici kaydet
    uzanti   = os.path.splitext(file.filename)[1]
    temp_yol = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{uzanti}")

    with open(temp_yol, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 4. Analiz et
    try:
        sonuc = sayac_analiz_et(temp_yol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_yol):
            os.remove(temp_yol)

    # 5. Sonuca kim gönderdi bilgisini ekle
    sonuc["kullanici"] = kullanici

    return JSONResponse(content=sonuc)
