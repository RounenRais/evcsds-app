import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

import cv2
from ultralytics import YOLO
from paddleocr import PaddleOCR
from rapidfuzz import fuzz

# ─── Yollar ───────────────────────────────────────────────────────────────────
# __file__ → "Bu script neredeyse orası"
# Böylece script hangi bilgisayarda çalışırsa çalışsın yolu otomatik bulur
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "runs", "detect", "runs",
                          "electric_meter_detection3", "weights", "best.pt")

# ─── Model ve OCR (bir kez yükle, her istekte tekrar yükleme) ─────────────────
# Bu satırlar modülü import edince çalışır, her analiz isteğinde değil
# Çünkü model yüklemek ~2-3 saniye sürer, her istekte yaparsak çok yavaş olur
model = YOLO(MODEL_PATH)

ocr = PaddleOCR(
    use_textline_orientation=True,
    lang="tr",
    device="gpu",
    text_det_thresh=0.3,
    text_det_box_thresh=0.4,
)


# ─── Yardımcı Fonksiyonlar ────────────────────────────────────────────────────

def ocr_metinleri_topla(ocr_result: list, min_score: float = 0.25) -> list:
    """
    PaddleOCR çıktısını temizleyip liste olarak döndürür.
    print() yok — veriyi döndürüyoruz, API kullanacak.

    Dönen format:
        [{"text": "1 FAZLI", "score": 0.80}, ...]
    """
    metinler = []
    if not ocr_result:
        return metinler

    for item in ocr_result:
        texts  = item["rec_texts"]
        scores = item["rec_scores"]
        for text, score in zip(texts, scores):
            text = text.strip()
            if score >= min_score and len(text) > 1:
                metinler.append({"text": text, "score": round(score, 2)})

    return metinler


def faz_tespit_et(metinler: list) -> dict:
    """
    OCR metinlerinden faz bilgisini çıkarır.

    Nasıl çalışır:
        1. Tüm metinleri tek bir string'e birleştirir
        2. rapidfuzz ile "1 FAZLI" ve "3 FAZLI" ifadelerine benzerlik skoru hesaplar
        3. En yüksek skora göre karar verir

    Dönen format:
        {"faz": "monofaz", "guvenskor": 92}
        {"faz": "trifaz",  "guvenskor": 88}
        {"faz": "belirsiz","guvenskor": 0 }
    """
    # Tüm metinleri birleştir → "1 PAZLI 2 TELLIAKTIF 240V LSM10..."
    tam_metin = " ".join(m["text"] for m in metinler).upper()

    # rapidfuzz: partial_ratio → kısa ifadeyi uzun metnin içinde arar
    # Örnek: "1 FAZLI" metinde "1 PAZLI" geçiyorsa → 92 puan verir
    monofaz_skoru = fuzz.partial_ratio("1 FAZLI", tam_metin)
    trifaz_skoru  = fuzz.partial_ratio("3 FAZLI", tam_metin)

    ESIK = 70  # 70 puan altı → eşleşme yok say

    if monofaz_skoru >= ESIK or trifaz_skoru >= ESIK:
        if monofaz_skoru >= trifaz_skoru:
            return {"faz": "monofaz", "guvenskor": monofaz_skoru}
        else:
            return {"faz": "trifaz", "guvenskor": trifaz_skoru}

    return {"faz": "belirsiz", "guvenskor": 0}


# ─── Ana Fonksiyon ────────────────────────────────────────────────────────────

def sayac_analiz_et(gorsel_yolu: str) -> dict:
    """
    Tek bir fotoğrafı analiz eder, sonucu dict olarak döndürür.
    FastAPI bu fonksiyonu çağıracak.

    Dönen format:
    {
        "sayac_bulundu": True,
        "yolo_guveni": 0.91,
        "faz": "monofaz",
        "faz_guvenskor": 92,
        "ocr_metinleri": [{"text": "1 FAZLI", "score": 0.80}, ...]
    }
    """
    img = cv2.imread(gorsel_yolu)
    if img is None:
        return {"hata": f"Görsel okunamadı: {gorsel_yolu}"}

    # ── Adım 1: YOLO ile sayacı bul ──────────────────────────────────────────
    results = model.predict(source=gorsel_yolu, conf=0.5, verbose=False)

    sayac_bulundu = False
    yolo_guveni   = 0.0
    ocr_metinleri = []

    for result in results:
        if result.boxes is None or len(result.boxes) == 0:
            continue

        # En yüksek güvenli kutuyu al (birden fazla sayaç varsa)
        en_iyi_box = max(result.boxes, key=lambda b: float(b.conf[0]))

        sayac_bulundu = True
        yolo_guveni   = round(float(en_iyi_box.conf[0]), 2)
        x1, y1, x2, y2 = map(int, en_iyi_box.xyxy[0])

        # ── Adım 2: Sayaç bölgesini kırp ─────────────────────────────────────
        margin = 60
        h, w   = img.shape[:2]
        crop   = img[
            max(0, y1 - margin) : min(h, y2 + margin),
            max(0, x1 - margin) : min(w, x2 + margin)
        ]

        # ── Adım 3: OCR ile yazıları oku ─────────────────────────────────────
        try:
            ocr_crop = list(ocr.predict(crop))
            ocr_metinleri = ocr_metinleri_topla(ocr_crop)
        except Exception as e:
            return {"hata": f"OCR hatası: {str(e)}"}

    # ── Adım 4: Faz tespiti ───────────────────────────────────────────────────
    if sayac_bulundu and ocr_metinleri:
        faz_sonucu = faz_tespit_et(ocr_metinleri)
    else:
        faz_sonucu = {"faz": "belirsiz", "guvenskor": 0}

    return {
        "sayac_bulundu" : sayac_bulundu,
        "yolo_guveni"   : yolo_guveni,
        "faz"           : faz_sonucu["faz"],
        "faz_guvenskor" : faz_sonucu["guvenskor"],
        "ocr_metinleri" : ocr_metinleri,
    }


# ─── Terminalde test için ─────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Kullanım: python predict_and_ocr.py <gorsel_yolu>")
        sys.exit(1)

    gorsel = sys.argv[1]
    sonuc  = sayac_analiz_et(gorsel)
    print(json.dumps(sonuc, ensure_ascii=False, indent=2))
