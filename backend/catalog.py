"""Araç ve wallbox kataloğunu okur; arama ve özet görünümleri üretir.

Katalog dosyaları `kds` branch'inden gelir ve çalışma sırasında değiştirilmez.
Kayıtlar süreç ömrü boyunca bir kez okunup bellekte tutulur.
"""

from __future__ import annotations

import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

ARAC_DOSYASI = DATA_DIR / "ARAC_KDS_CEKIRDEK_100.json"
WALLBOX_DOSYASI = DATA_DIR / "WALLBOX_KDS_CEKIRDEK_30_V1_1.json"

# Listeleme yanıtında dönen alanlar. Katalogdaki diğer alanlar yalnız motor
# tarafında kullanılır; arayüze taşınmaz.
ARAC_OZET_ALANLARI = (
    "vehicle_id",
    "marka",
    "model",
    "ac_konnektor_tipi",
    "ac_tek_faz_azami_guc_kw",
    "ac_uc_faz_azami_guc_kw",
    "batarya_kullanilabilir_kwh",
    "wltp_tuketim_kwh_100km",
    "wltp_menzil_km",
)
WALLBOX_OZET_ALANLARI = (
    "charger_id",
    "marka",
    "model",
    "nominal_azami_guc_kw",
    "ac_konnektor_tipi",
    "baglanti_tipi",
    "kablo_uzunlugu_m",
    "ip_sinifi",
    "dinamik_yuk_yonetimi_destegi",
    "fiyat_tl",
    "fiyat_tarihi",
    "garanti_yil",
)


class KatalogHatasi(RuntimeError):
    """Katalog dosyası okunamadığında veya tutarsız olduğunda yükselir."""


def _json_oku(yol: Path) -> list[dict[str, Any]]:
    if not yol.is_file():
        raise KatalogHatasi(f"Katalog dosyası bulunamadı: {yol}")
    try:
        with yol.open(encoding="utf-8-sig") as dosya:
            icerik = json.load(dosya)
    except json.JSONDecodeError as hata:
        raise KatalogHatasi(f"Katalog dosyası bozuk: {yol}") from hata
    if not isinstance(icerik, list):
        raise KatalogHatasi(f"Katalog dosyası liste değil: {yol}")
    return icerik


def _indeksle(kayitlar: list[dict[str, Any]], anahtar: str) -> dict[str, dict[str, Any]]:
    indeks: dict[str, dict[str, Any]] = {}
    for kayit in kayitlar:
        deger = kayit.get(anahtar)
        if not isinstance(deger, str) or not deger.strip():
            raise KatalogHatasi(f"Kayıtta geçersiz {anahtar}: {deger!r}")
        if deger in indeks:
            raise KatalogHatasi(f"Tekrarlı {anahtar}: {deger}")
        indeks[deger] = kayit
    return indeks


@lru_cache(maxsize=1)
def araclar() -> dict[str, dict[str, Any]]:
    return _indeksle(_json_oku(ARAC_DOSYASI), "vehicle_id")


@lru_cache(maxsize=1)
def wallboxlar() -> dict[str, dict[str, Any]]:
    return _indeksle(_json_oku(WALLBOX_DOSYASI), "charger_id")


def normalize_et(metin: str) -> str:
    """Türkçe duyarlı arama anahtarı üretir.

    Noktalı ve noktasız i (`İ I ı`) tek harfe indirilir: kullanıcı `ıonıq` da
    yazsa `IONIQ` da bulunur, `id3` araması `ID.3` ile eşleşir. Noktalama ve
    boşluk atılır.
    """
    for harf in ("İ", "I", "ı"):
        metin = metin.replace(harf, "i")
    metin = metin.lower()
    metin = unicodedata.normalize("NFKD", metin)
    return "".join(k for k in metin if k.isalnum())


def _ozet(kayit: dict[str, Any], alanlar: tuple[str, ...]) -> dict[str, Any]:
    return {alan: kayit.get(alan) for alan in alanlar}


def arac_listesi(sorgu: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
    """Marka ve modelde arar. Sorgu boşsa katalogdaki sırayla tümünü döndürür."""
    kayitlar = list(araclar().values())
    if sorgu:
        anahtar = normalize_et(sorgu)
        if anahtar:
            kayitlar = [
                kayit
                for kayit in kayitlar
                if anahtar in normalize_et(f"{kayit.get('marka', '')}{kayit.get('model', '')}")
            ]
    if limit is not None:
        kayitlar = kayitlar[:limit]
    return [_ozet(kayit, ARAC_OZET_ALANLARI) for kayit in kayitlar]


def wallbox_listesi() -> list[dict[str, Any]]:
    return [_ozet(kayit, WALLBOX_OZET_ALANLARI) for kayit in wallboxlar().values()]


def arac_getir(vehicle_id: str) -> dict[str, Any] | None:
    return araclar().get(vehicle_id)


def wallbox_ozeti(charger_id: str) -> dict[str, Any]:
    """Sonuç listesinde ürünü tanıtmak için kullanılan alanlar."""
    kayit = wallboxlar().get(charger_id)
    if kayit is None:
        return {"charger_id": charger_id}
    return _ozet(kayit, WALLBOX_OZET_ALANLARI)


def katalog_durumu() -> dict[str, Any]:
    """/health için: katalog okunabiliyor mu, kaç kayıt var."""
    try:
        return {
            "okunabilir": True,
            "arac_sayisi": len(araclar()),
            "wallbox_sayisi": len(wallboxlar()),
        }
    except KatalogHatasi as hata:
        return {"okunabilir": False, "hata": str(hata)}
