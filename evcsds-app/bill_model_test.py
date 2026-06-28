import os

import cv2
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


def resolve_image_folder(path):
    images_path = os.path.join(path, "images")
    if os.path.isdir(images_path):
        return images_path
    return path


def resolve_model_path():
    if os.path.exists(CLEAN_BILL_MODEL_PATH):
        return CLEAN_BILL_MODEL_PATH
    return LEGACY_BILL_MODEL_PATH


def predict_images(image_folder):
    model = YOLO(resolve_model_path())

    images = [f for f in os.listdir(image_folder) if f.endswith((".jpg", ".jpeg", ".png"))]

    if not images:
        print("bill_test_images klasöründe işlenecek görsel yok.")
        return

    for img_name in images:
        img_path = os.path.join(image_folder, img_name)
        results = model.predict(img_path, conf=DETECTION_CONF)

        for result in results:
            img = cv2.imread(img_path)

            if len(result.boxes) == 0:
                print(f"{img_name}: ❌ Fatura bulunamadı")
                cv2.putText(
                    img,
                    "Fatura YOK",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                )
            else:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])

                    print(
                        f"{img_name}: ✅ Fatura bulundu! Güven: {conf:.2f} | Konum: ({x1},{y1}) - ({x2},{y2})"
                    )

                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(
                        img,
                        f"Fatura {conf:.2f}",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.9,
                        (0, 255, 0),
                        2,
                    )

            output_path = os.path.join(image_folder, f"result_{img_name}")
            cv2.imwrite(output_path, img)

            cv2.imshow(img_name, img)
            print("Devam etmek için herhangi bir tuşa bas...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        print("-" * 50)
if __name__ == "__main__":
    varsayilan_klasor = os.path.join(BASE_DIR, "bill_test_images")
    predict_images(resolve_image_folder(varsayilan_klasor))