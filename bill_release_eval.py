"""Fatura alanlarını kişisel veri içermeyen saha etiketleriyle ölçer.

OCR metni/görseli kaydetmez; yalnız alan bazında sayım ve süreleri yazdırır.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
ALANLAR = ("sozlesme_gucu_kw", "donem_tuketimi_kwh", "tarife")
DURUMLAR = {"dogrulandi", "belgede_yok", "dogrulanmadi"}
ZORUNLU_SUTUNLAR = {
    "ornek_id", "gorsel_yolu", "bagimsiz_test", "fatura_var",
    *(f"{alan}_durum" for alan in ALANLAR), *ALANLAR,
}


def manifesti_oku(yol: Path) -> list[dict[str, str]]:
    with yol.open(encoding="utf-8-sig", newline="") as dosya:
        okuyucu = csv.DictReader(dosya)
        eksik = ZORUNLU_SUTUNLAR - set(okuyucu.fieldnames or [])
        if eksik:
            raise ValueError(f"Eksik sütunlar: {', '.join(sorted(eksik))}")
        satirlar = list(okuyucu)
    if not satirlar:
        raise ValueError("Etiket tablosu boş.")

    gorulen = set()
    for satir in satirlar:
        kimlik = satir["ornek_id"].strip()
        if not kimlik or kimlik in gorulen:
            raise ValueError("Örnek kimlikleri benzersiz ve dolu olmalı.")
        gorulen.add(kimlik)
        if satir["bagimsiz_test"] not in {"evet", "hayir", "bilinmiyor"}:
            raise ValueError(f"{kimlik}: bagimsiz_test geçersiz.")
        if satir["fatura_var"] not in {"evet", "hayir"}:
            raise ValueError(f"{kimlik}: fatura_var geçersiz.")
        gorsel = (BASE_DIR / satir["gorsel_yolu"]).resolve()
        if not gorsel.is_file():
            raise ValueError(f"{kimlik}: görsel bulunamadı: {gorsel}")
        for alan in ALANLAR:
            durum = satir[f"{alan}_durum"]
            deger = satir[alan].strip()
            if durum not in DURUMLAR:
                raise ValueError(f"{kimlik}: {alan} durumu geçersiz.")
            if durum == "dogrulandi" and not deger:
                raise ValueError(f"{kimlik}: doğrulanmış {alan} değeri boş.")
            if durum != "dogrulandi" and deger:
                raise ValueError(f"{kimlik}: doğrulanmamış {alan} değeri dolu.")
            if durum == "dogrulandi" and alan != "tarife":
                try:
                    sayi = float(deger)
                except ValueError as exc:
                    raise ValueError(
                        f"{kimlik}: {alan} değeri ondalık noktayla sayı olmalı."
                    ) from exc
                if not math.isfinite(sayi) or sayi < 0:
                    raise ValueError(f"{kimlik}: {alan} sayısı geçersiz.")
        if satir["fatura_var"] == "hayir" and any(
            satir[f"{alan}_durum"] != "dogrulanmadi" for alan in ALANLAR
        ):
            raise ValueError(f"{kimlik}: fatura olmayan görselde alan etiketi olamaz.")
    return satirlar


def kullanilabilir_aday(analiz: dict[str, Any], alan: str) -> Any:
    if analiz.get("fatura_bulundu") is not True:
        return None
    bilgiler = analiz.get("fatura_bilgileri") or {}
    if alan in bilgiler.get("manuel_giris_alanlari", []):
        return None
    kanit = (bilgiler.get("alanlar") or {}).get(alan) or {}
    try:
        guven = float(kanit.get("guven", 0))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(guven) or guven < 0.70:
        return None
    return kanit.get("deger")


def alan_sonucu(alan: str, durum: str, gercek: str, aday: Any) -> str | None:
    """Doğrulanmamış etiketleri skor dışında bırakır."""
    if durum == "dogrulanmadi":
        return None
    if durum == "belgede_yok":
        return "yanlis_dolu" if aday is not None else "dogru_bos"
    if aday is None:
        return "kacirildi"
    if alan == "tarife":
        dogru = aday == gercek
    else:
        try:
            dogru = math.isclose(
                float(aday), float(gercek), rel_tol=0,
                abs_tol=0.001 if alan == "sozlesme_gucu_kw" else 0.01,
            )
        except (TypeError, ValueError):
            dogru = False
    return "dogru_dolu" if dogru else "yanlis_dolu"


def degerlendir(satirlar: list[dict[str, str]]) -> dict:
    # Geç import: --validate-only model/OCR yüklemeden etiketleri denetleyebilir.
    from bill_predict_and_ocr import fatura_analiz_et
    from image_processing import MAX_UPLOAD_BYTES, gorseli_hazirla

    def bos_kohort() -> dict:
        return {
            "ornek_sayisi": 0,
            "tespit": {"dogru": 0, "yanlis": 0},
            "alanlar": {
                alan: {
                    sonuc: 0
                    for sonuc in ("dogru_dolu", "yanlis_dolu", "kacirildi", "dogru_bos")
                }
                for alan in ALANLAR
            },
            "sureler": [],
        }

    kohortlar = {"tum_ornekler": bos_kohort(), "bagimsiz_test": bos_kohort()}
    with tempfile.TemporaryDirectory(prefix="evcsds_bill_eval_") as gecici:
        for satir in satirlar:
            gorsel = BASE_DIR / satir["gorsel_yolu"]
            if gorsel.stat().st_size > MAX_UPLOAD_BYTES:
                raise ValueError(f"{satir['ornek_id']}: görsel 25 MB sınırını aşıyor.")
            gecici_yol, _ = gorseli_hazirla(gorsel.read_bytes(), Path(gecici))
            baslangic = time.perf_counter()
            analiz = fatura_analiz_et(gecici_yol)
            sure = round(time.perf_counter() - baslangic, 2)
            bulundu = analiz.get("fatura_bulundu") is True
            beklenen = satir["fatura_var"] == "evet"
            alan_durumlari = {}
            hedefler = [kohortlar["tum_ornekler"]]
            if satir["bagimsiz_test"] == "evet":
                hedefler.append(kohortlar["bagimsiz_test"])
            for kohort in hedefler:
                kohort["ornek_sayisi"] += 1
                kohort["sureler"].append(sure)
                kohort["tespit"]["dogru" if bulundu == beklenen else "yanlis"] += 1
                if beklenen:
                    for alan in ALANLAR:
                        sonuc = alan_sonucu(
                            alan, satir[f"{alan}_durum"], satir[alan],
                            kullanilabilir_aday(analiz, alan),
                        )
                        if sonuc is not None:
                            kohort["alanlar"][alan][sonuc] += 1
                            alan_durumlari[alan] = sonuc
            print(
                f"{satir['ornek_id']}: tespit={bulundu}, "
                f"alanlar={alan_durumlari}, "
                f"adaylar={{'sozlesme_gucu_kw': {kullanilabilir_aday(analiz, 'sozlesme_gucu_kw')!r}, "
                f"'donem_tuketimi_kwh': {kullanilabilir_aday(analiz, 'donem_tuketimi_kwh')!r}, "
                f"'tarife': {kullanilabilir_aday(analiz, 'tarife')!r}}}, "
                f"süre={sure} sn",
                flush=True,
            )
    for kohort in kohortlar.values():
        sureler = kohort.pop("sureler")
        kohort["sure_p50_sn"] = statistics.median(sureler) if sureler else None
        kohort["sure_p95_sn"] = (
            sorted(sureler)[math.ceil(len(sureler) * 0.95) - 1] if sureler else None
        )
    return {
        "kohortlar": kohortlar,
        "uyari": "Bağımsız kaynak ve çift kontrollü gerçek değerler olmadan yayına hazır sonucu çıkarılamaz.",
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "manifest", nargs="?", type=Path,
        default=BASE_DIR / "planning" / "FATURA_SAHA_DOGRULAMA_SABLONU.csv",
    )
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    satirlar = manifesti_oku(args.manifest)
    puanlanabilir_etiket = sum(
        satir[f"{alan}_durum"] != "dogrulanmadi"
        for satir in satirlar for alan in ALANLAR
    )
    bagimsiz = sum(satir["bagimsiz_test"] == "evet" for satir in satirlar)
    print(
        f"Etiket tablosu geçerli: {len(satirlar)} örnek, "
        f"{puanlanabilir_etiket} puanlanabilir alan etiketi, {bagimsiz} bağımsız örnek"
    )
    if not args.validate_only:
        print(json.dumps(degerlendir(satirlar), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
