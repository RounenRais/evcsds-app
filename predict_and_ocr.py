import os
os.environ["PADDLE_PDX_CACHE_HOME"] = r"C:\paddleocr_models\paddlex"
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"

import cv2
import numpy as np
import matplotlib.pyplot as plt
from ultralytics import YOLO
from paddleocr import PaddleOCR

MODEL_PATH = r"C:\EASIOS\runs\detect\runs\electric_meter_detection3\weights\best.pt"
IMAGE_FOLDER = r"C:\EASIOS\test_images"


def ocr_sonuclari_yazdir(ocr_result):
    text_found = False
    if not ocr_result:
        print("  Metin okunamadı.")
        return
    for item in ocr_result:
        texts = item["rec_texts"]
        scores = item["rec_scores"]
        for text, score in zip(texts, scores):
            text = text.strip()
            if score >= 0.25 and len(text) > 1:
                text_found = True
                print(f"  {text}   (güven: {score:.2f})")
    if not text_found:
        print("  Metin okunamadı.")


def predict_and_ocr(image_folder):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"YOLO model bulunamadı: {MODEL_PATH}")

    model = YOLO(MODEL_PATH)

    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang="tr",
        device="cpu",
        text_det_thresh=0.3,
        text_det_box_thresh=0.4,
    )

    images = [
        f for f in os.listdir(image_folder)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
        and not f.startswith("result_")
    ]

    if not images:
        print("Klasörde işlenecek görsel yok.")
        return

    for img_name in images:
        img_path = os.path.join(image_folder, img_name)
        img = cv2.imread(img_path)

        if img is None:
            print(f"Resim okunamadı: {img_name}")
            continue

        print("\n" + "=" * 60)
        print(f"Resim: {img_name}")
        print("=" * 60)

        results = model.predict(source=img_path, conf=0.5, verbose=False)

        crop = None
        meter_found = False

        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue

            for i, box in enumerate(result.boxes):
                meter_found = True
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.putText(
                    img, f"Sayac {conf:.2f}",
                    (x1, max(30, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
                )

                margin = 60
                h, w = img.shape[:2]
                # Renkli crop - OCR için
                crop = img[
                    max(0, y1 - margin):min(h, y2 + margin),
                    max(0, x1 - margin):min(w, x2 + margin)
                ]

                print(f"\n✅ Sayaç #{i+1} (güven: {conf:.2f})")

                print("\n📋 [CROP] Okunan yazılar:")
                print("-" * 40)
                try:
                    ocr_result_crop = list(ocr.predict(crop))
                    ocr_sonuclari_yazdir(ocr_result_crop)
                except Exception as e:
                    print(f"  OCR hatası: {e}")

                print("\n📋 [TAM RESİM] Okunan yazılar:")
                print("-" * 40)
                try:
                    ocr_result_tam = list(ocr.predict(img))
                    ocr_sonuclari_yazdir(ocr_result_tam)
                except Exception as e:
                    print(f"  OCR hatası: {e}")

        if not meter_found:
            print("❌ Sayaç bulunamadı.")

        fig, axes = plt.subplots(1, 2, figsize=(16, 8))
        axes[0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        axes[0].set_title(f"Tespit: {img_name}", fontsize=12)
        axes[0].axis("off")

        if crop is not None:
            axes[1].imshow(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
            axes[1].set_title("Sayaç Yakın Çekim", fontsize=12)
            axes[1].axis("off")

        plt.tight_layout()
        save_path = os.path.join(image_folder, f"result_{img_name}")
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        print(f"\nKaydedildi: {save_path}")


if __name__ == "__main__":
    predict_and_ocr(IMAGE_FOLDER)