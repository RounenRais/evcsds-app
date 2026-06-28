import os

from ultralytics import YOLO


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_YAML = os.path.join(BASE_DIR, "bill_dataset_clean", "data.yaml")


def main():
    model = YOLO("yolo11n.pt")

    model.train(
        data=DATASET_YAML,
        epochs=100,
        imgsz=640,
        batch=8,
        device="cpu",
        project="runs",
        name="electricity_bill_detection_clean1",
        pretrained=True,
        verbose=True,
        augment=True,
        patience=20,
        exist_ok=False,
    )


if __name__ == "__main__":
    main()