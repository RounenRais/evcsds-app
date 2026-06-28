import json
import os
import sys

os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["PADDLE_PDX_CACHE_HOME"] = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    ".paddlex",
)

import cv2
from paddleocr import PaddleOCR
from ultralytics import YOLO


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DETECTION_CONF = 0.25
LEGACY_BILL_MODEL_PATH = os.path.join(
    BASE_DIR,
    "runs",
    "detect",
    "runs",
    "electricity_bill_detection1-2",
    "weights",
    "best.pt",
)
CLEAN_BILL_MODEL_PATH = os.path.join(
    BASE_DIR,
    "runs",
    "detect",
    "runs",
    "electricity_bill_detection_clean1",
    "weights",
    "best.pt",
)


def resolve_image_folder(path: str) -> str:
    images_path = os.path.join(path, "images")
    if os.path.isdir(images_path):
        return images_path
    return path


def resolve_model_path() -> str:
    if os.path.exists(CLEAN_BILL_MODEL_PATH):
        return CLEAN_BILL_MODEL_PATH
    return LEGACY_BILL_MODEL_PATH

model = YOLO(resolve_model_path())

ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="tr",
    device="cpu",
    engine="transformers",
    text_det_thresh=0.3,
    text_det_box_thresh=0.4,
)


def ocr_metinleri_topla(ocr_result: list, min_score: float = 0.25) -> list:
    metinler = []
    if not ocr_result:
        return metinler

    for item in ocr_result:
        texts = item["rec_texts"]
        scores = item["rec_scores"]
        for text, score in zip(texts, scores):
            text = text.strip()
            if score >= min_score and len(text) > 1:
                metinler.append({"text": text, "score": round(score, 2)})

    return metinler


def faturayi_isaretle(gorsel_yolu: str, sonuc: dict) -> str | None:
    img = cv2.imread(gorsel_yolu)
    if img is None:
        return None

    if sonuc.get("fatura_bulundu"):
        x1 = sonuc.get("bbox_x1")
        y1 = sonuc.get("bbox_y1")
        x2 = sonuc.get("bbox_x2")
        y2 = sonuc.get("bbox_y2")
        guven = sonuc.get("yolo_guveni", 0.0)

        if None not in (x1, y1, x2, y2):
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
            etiket = f"Fatura {guven:.2f}"
            etiket_y = max(30, y1 - 10)
            cv2.putText(
                img,
                etiket,
                (x1, etiket_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )
    else:
        cv2.putText(
            img,
            "Fatura YOK",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )

    klasor = os.path.dirname(gorsel_yolu)
    cikti_adi = f"result_{os.path.basename(gorsel_yolu)}"
    cikti_yolu = os.path.join(klasor, cikti_adi)
    cv2.imwrite(cikti_yolu, img)
    return cikti_yolu


def fatura_analiz_et(gorsel_yolu: str) -> dict:
    img = cv2.imread(gorsel_yolu)
    if img is None:
        return {"hata": f"Görsel okunamadı: {gorsel_yolu}"}

    results = model.predict(source=gorsel_yolu, conf=DETECTION_CONF, verbose=False)

    fatura_bulundu = False
    yolo_guveni = 0.0
    ocr_metinleri = []
    bbox_x1 = bbox_y1 = bbox_x2 = bbox_y2 = None

    for result in results:
        if result.boxes is None or len(result.boxes) == 0:
            continue

        en_iyi_box = max(result.boxes, key=lambda b: float(b.conf[0]))
        fatura_bulundu = True
        yolo_guveni = round(float(en_iyi_box.conf[0]), 2)
        bbox_x1, bbox_y1, bbox_x2, bbox_y2 = map(int, en_iyi_box.xyxy[0])

        margin = 60
        h, w = img.shape[:2]
        crop = img[
            max(0, bbox_y1 - margin) : min(h, bbox_y2 + margin),
            max(0, bbox_x1 - margin) : min(w, bbox_x2 + margin),
        ]

        try:
            ocr_crop = list(ocr.predict(crop))
            ocr_metinleri = ocr_metinleri_topla(ocr_crop)
        except Exception as e:
            return {"hata": f"OCR hatası: {str(e)}"}

    return {
        "fatura_bulundu": fatura_bulundu,
        "yolo_guveni": yolo_guveni,
        "ocr_metinleri": ocr_metinleri,
        "bbox_x1": bbox_x1,
        "bbox_y1": bbox_y1,
        "bbox_x2": bbox_x2,
        "bbox_y2": bbox_y2,
    }


if __name__ == "__main__":
    def yazdir_sonuc(gorsel_yolu: str) -> None:
        sonuc = fatura_analiz_et(gorsel_yolu)
        cikti_yolu = faturayi_isaretle(gorsel_yolu, sonuc)
        print(f"\n=== {os.path.basename(gorsel_yolu)} ===")
        print(json.dumps(sonuc, ensure_ascii=False, indent=2))
        if cikti_yolu:
            print(f"Kaydedildi: {cikti_yolu}")

    if len(sys.argv) < 2:
        varsayilan_klasor = os.path.join(BASE_DIR, "bill_test_images")
        print(f"Argüman verilmedi, varsayılan klasör kullanılıyor: {varsayilan_klasor}")

        if not os.path.isdir(varsayilan_klasor):
            print("bill_test_images klasörü bulunamadı.")
            sys.exit(1)

        gorseller = [
            os.path.join(varsayilan_klasor, dosya)
            for dosya in sorted(os.listdir(varsayilan_klasor))
            if dosya.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))
        ]

        if not gorseller:
            print("Fatura test klasöründe işlenecek görsel yok.")
            sys.exit(1)

        for gorsel in gorseller:
            yazdir_sonuc(gorsel)
    else:
        hedef = resolve_image_folder(sys.argv[1])

        if os.path.isdir(hedef):
            gorseller = [
                os.path.join(hedef, dosya)
                for dosya in sorted(os.listdir(hedef))
                if dosya.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp"))
            ]

            if not gorseller:
                print("Verilen klasörde işlenecek görsel yok.")
                sys.exit(1)

            for gorsel in gorseller:
                yazdir_sonuc(gorsel)
        else:
            yazdir_sonuc(hedef)