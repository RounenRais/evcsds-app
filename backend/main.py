"""EVCSDS birleşik API.

İki katmanı tek serviste birleştirir:

* `vision/`  — sayaç ve fatura görsellerinden teknik alanları okur (YOLO + OCR).
* `kds_engine/` — okunan ev bilgisi, araç ve kullanım girdisiyle 30 wallbox'ı
  dört gruba ayırır ve M01–M06 metriklerini hesaplar.

Görsel katmanı bilerek tembel yüklenir: torch ve paddleocr birkaç GB'lık
bağımlılıklardır ve katalog/öneri uçları onlarsız da çalışır.

Çalıştırma (bu dosyanın bulunduğu klasörden):
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
"""

from __future__ import annotations

import asyncio
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

os.environ.setdefault("YOLO_AUTOINSTALL", "false")

import catalog
import recommend
from key_utils import key_gecerli_mi, key_sahibi, key_uret


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "temp_uploads"
ADMIN_KEY = os.getenv("EVCSDS_ADMIN_KEY")

# YOLO modelleri GPU belleğinde durduğu için aynı anda tek analiz çalışır.
MAX_CONCURRENT_ANALYSES = 1

logging.basicConfig(
    level=os.getenv("EVCSDS_LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("evcsds.api")
analiz_semaforu = asyncio.Semaphore(MAX_CONCURRENT_ANALYSES)

frontend_originleri = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app = FastAPI(
    title="EVCSDS API",
    description="Görsel analiz ve ev tipi AC wallbox karar desteği.",
    version="3.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_originleri,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------
# Görsel katmanı — tembel yükleme
# --------------------------------------------------------------------------

_gorsel_modulleri: dict[str, Any] | None = None
_gorsel_hatasi: str | None = None


def gorsel_katmani() -> dict[str, Any]:
    """Görsel analiz modüllerini ilk istekte yükler ve sonraki çağrılarda yeniden kullanır."""
    global _gorsel_modulleri, _gorsel_hatasi
    if _gorsel_modulleri is not None:
        return _gorsel_modulleri
    if _gorsel_hatasi is not None:
        raise HTTPException(status_code=503, detail=_gorsel_hatasi)
    try:
        from vision.bill_predict_and_ocr import MODEL_PATH as fatura_modeli
        from vision.bill_predict_and_ocr import fatura_analiz_et
        from vision.home_input import kds_ev_girdisi_olustur
        from vision.image_processing import (
            GorselDogrulamaHatasi,
            gorseli_hazirla,
            upload_verisini_oku,
        )
        from vision.predict_and_ocr import MODEL_PATH as sayac_modeli
        from vision.predict_and_ocr import sayac_analiz_et
    except Exception as hata:  # ImportError, FileNotFoundError, OSError...
        _gorsel_hatasi = (
            "Görsel analiz katmanı bu kurulumda kullanılamıyor. "
            "requirements-vision.txt bağımlılıkları ve backend/models altındaki "
            f"model ağırlıkları gerekir. Ayrıntı: {hata}"
        )
        logger.exception("Görsel analiz katmanı yüklenemedi")
        raise HTTPException(status_code=503, detail=_gorsel_hatasi) from hata

    _gorsel_modulleri = {
        "sayac_analiz_et": sayac_analiz_et,
        "fatura_analiz_et": fatura_analiz_et,
        "kds_ev_girdisi_olustur": kds_ev_girdisi_olustur,
        "gorseli_hazirla": gorseli_hazirla,
        "upload_verisini_oku": upload_verisini_oku,
        "GorselDogrulamaHatasi": GorselDogrulamaHatasi,
        "sayac_modeli": sayac_modeli,
        "fatura_modeli": fatura_modeli,
    }
    return _gorsel_modulleri


def gorsel_katmani_durumu() -> dict[str, Any]:
    """/health için: ağır bağımlılıkları yüklemeden ağırlık dosyalarını kontrol eder."""
    agirliklar = {
        "sayac": (BASE_DIR / "models" / "sayac_yolo.pt").is_file(),
        "fatura": (BASE_DIR / "models" / "fatura_yolo.pt").is_file(),
    }
    return {
        "model_agirliklari": agirliklar,
        "agirliklar_tam": all(agirliklar.values()),
        "yuklendi": _gorsel_modulleri is not None,
        "yukleme_hatasi": _gorsel_hatasi,
    }


# --------------------------------------------------------------------------
# Kimlik doğrulama
# --------------------------------------------------------------------------

def api_key_dogrula(api_key: str | None) -> str:
    if not api_key:
        raise HTTPException(
            status_code=401, detail="API key gerekli. X-API-Key header'ını gönderin."
        )
    if not key_gecerli_mi(api_key):
        raise HTTPException(status_code=401, detail="Geçersiz API key.")
    return key_sahibi(api_key) or "bilinmeyen"


# --------------------------------------------------------------------------
# Görsel analiz uçları
# --------------------------------------------------------------------------

async def _gorsel_analiz_et(
    file: UploadFile,
    x_api_key: str | None,
    analiz_adi: str,
    analiz_turu: str,
) -> dict:
    kullanici = api_key_dogrula(x_api_key)
    gorsel = gorsel_katmani()
    analiz_fonksiyonu: Callable[[str | Path], dict] = gorsel[analiz_adi]
    gecici_yol: Path | None = None

    try:
        veri = await gorsel["upload_verisini_oku"](file)
        gecici_yol, gorsel_bilgisi = await run_in_threadpool(
            gorsel["gorseli_hazirla"], veri, UPLOAD_DIR
        )

        baslangic = time.perf_counter()
        async with analiz_semaforu:
            sonuc = await run_in_threadpool(analiz_fonksiyonu, gecici_yol)
        sure_ms = round((time.perf_counter() - baslangic) * 1000)

        sonuc["analiz_turu"] = analiz_turu
        sonuc["kullanici"] = kullanici
        sonuc["islem_suresi_ms"] = sure_ms
        sonuc["gorsel"] = gorsel_bilgisi.dict()
        return sonuc
    except gorsel["GorselDogrulamaHatasi"] as hata:
        durum = 413 if "25 MB" in str(hata) else 400
        raise HTTPException(status_code=durum, detail=str(hata)) from hata
    except HTTPException:
        raise
    except Exception:
        logger.exception("%s analizi sırasında beklenmeyen hata", analiz_turu)
        raise HTTPException(status_code=500, detail="Görsel analizi tamamlanamadı.")
    finally:
        await file.close()
        if gecici_yol is not None:
            try:
                gecici_yol.unlink(missing_ok=True)
            except OSError:
                logger.warning("Geçici dosya silinemedi: %s", gecici_yol)


@app.post("/analyze")
@app.post("/analyze/meter")
async def analyze_meter(
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict:
    return await _gorsel_analiz_et(file, x_api_key, "sayac_analiz_et", "sayac")


@app.post("/analyze/bill")
async def analyze_bill(
    file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict:
    return await _gorsel_analiz_et(file, x_api_key, "fatura_analiz_et", "fatura")


@app.post("/analyze/home")
async def analyze_home(
    meter_file: UploadFile = File(...),
    bill_file: UploadFile = File(...),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict:
    """İki görselden KDS ev girdisi üretir; ham OCR metinlerini döndürmez."""
    api_key_dogrula(x_api_key)
    gorsel = gorsel_katmani()
    baslangic = time.perf_counter()
    sayac_sonucu = await _gorsel_analiz_et(meter_file, x_api_key, "sayac_analiz_et", "sayac")
    fatura_sonucu = await _gorsel_analiz_et(bill_file, x_api_key, "fatura_analiz_et", "fatura")
    sonuc = gorsel["kds_ev_girdisi_olustur"](sayac_sonucu, fatura_sonucu)
    sonuc["islem_suresi_ms"] = round((time.perf_counter() - baslangic) * 1000)
    return sonuc


# --------------------------------------------------------------------------
# Katalog uçları
# --------------------------------------------------------------------------

@app.get("/catalog/vehicles")
def catalog_vehicles(
    q: str | None = Query(default=None, max_length=100, description="Marka veya model araması"),
    limit: int = Query(default=100, ge=1, le=100),
) -> dict:
    try:
        kayitlar = catalog.arac_listesi(q, limit)
    except catalog.KatalogHatasi as hata:
        raise HTTPException(status_code=500, detail=str(hata)) from hata
    return {"sayi": len(kayitlar), "araclar": kayitlar}


@app.get("/catalog/wallboxes")
def catalog_wallboxes() -> dict:
    try:
        kayitlar = catalog.wallbox_listesi()
    except catalog.KatalogHatasi as hata:
        raise HTTPException(status_code=500, detail=str(hata)) from hata
    return {"sayi": len(kayitlar), "wallboxlar": kayitlar}


# --------------------------------------------------------------------------
# Öneri ucu
# --------------------------------------------------------------------------

class EvGirdisi(BaseModel):
    faz: str = Field(description="monofaz, trifaz veya belirsiz")
    sozlesme_gucu_kw: float | None = Field(default=None, ge=0.5, le=100)
    donem_tuketimi_kwh: float | None = Field(default=None, ge=0, le=1_000_000)
    gunluk_ortalama_kwh: float | None = Field(default=None, ge=0, le=10_000)
    tarife: str | None = Field(default=None, max_length=120)


class KullanimGirdisi(BaseModel):
    gunluk_ortalama_km: float | None = Field(default=None, ge=0, le=2000)
    evde_sarj_icin_uygun_sure_saat: float | None = Field(default=None, ge=0, le=24)
    butce_tl: float | None = Field(default=None, ge=0, le=10_000_000)
    kurulum_yeri: str = Field(description="İç mekan veya Dış mekan")


class OneriIstegi(BaseModel):
    home: EvGirdisi
    vehicle_id: str = Field(min_length=1, max_length=200)
    user: KullanimGirdisi
    kullanici_onayladi: bool = Field(
        description=(
            "Ev bilgilerinin kullanıcı tarafından doğrulandığını belirtir. "
            "Görsel analiz çıktısı tek başına onay yerine geçmez."
        )
    )


@app.post("/recommend")
def recommend_endpoint(istek: OneriIstegi) -> dict:
    """Onaylanmış ev girdisi + araç + kullanım bilgisinden dört aday listesi üretir."""
    try:
        return recommend.oneri_uret(
            home=istek.home.model_dump(),
            vehicle_id=istek.vehicle_id,
            user=istek.user.model_dump(),
            kullanici_onayladi=istek.kullanici_onayladi,
        )
    except recommend.OneriGirdiHatasi as hata:
        raise HTTPException(status_code=400, detail=str(hata)) from hata
    except catalog.KatalogHatasi as hata:
        raise HTTPException(status_code=500, detail=str(hata)) from hata
    except ValueError as hata:
        # Motorun kendi NEED_INPUT / tekrarlı charger_id kontrolleri.
        logger.warning("Motor girdiyi reddetti: %s", hata)
        raise HTTPException(status_code=400, detail=str(hata)) from hata


# --------------------------------------------------------------------------
# Servis uçları
# --------------------------------------------------------------------------

@app.get("/")
def root() -> dict:
    return {
        "mesaj": "EVCSDS API çalışıyor",
        "versiyon": "3.0.0",
        "endpointler": [
            "/health",
            "/analyze/meter",
            "/analyze/bill",
            "/analyze/home",
            "/catalog/vehicles",
            "/catalog/wallboxes",
            "/recommend",
        ],
    }


@app.get("/health")
def health() -> dict:
    gorsel = gorsel_katmani_durumu()
    katalog = catalog.katalog_durumu()
    return {
        "durum": "ok" if katalog.get("okunabilir") else "hazir_degil",
        "karar_motoru": katalog,
        "gorsel_analiz": gorsel,
    }


@app.post("/keys/generate")
def generate_key(
    kullanici_adi: str = Query(min_length=2, max_length=100),
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
) -> dict:
    if not ADMIN_KEY:
        raise HTTPException(status_code=503, detail="API key üretimi sunucuda etkin değil.")
    if not x_admin_key or not secrets.compare_digest(x_admin_key, ADMIN_KEY):
        raise HTTPException(status_code=403, detail="Geçersiz yönetici anahtarı.")
    return {"kullanici": kullanici_adi, "api_key": key_uret(kullanici_adi)}
