from pathlib import Path

import torch
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent
DATASET_YAML = BASE_DIR / "new_electric_bills_model" / "data.yaml"
INITIAL_WEIGHTS = BASE_DIR / "yolo11n.pt"
RUNS_DIR = BASE_DIR / "runs" / "detect"
RUN_NAME = "electricity_bill_detection_v2"


def main() -> None:
    device: int | str = 0 if torch.cuda.is_available() else "cpu"
    model = YOLO(str(INITIAL_WEIGHTS))

    model.train(
        data=str(DATASET_YAML),
        epochs=100,
        imgsz=640,
        batch=8,
        device=device,
        project=str(RUNS_DIR),
        name=RUN_NAME,
        pretrained=True,
        verbose=True,
        augment=True,
        patience=20,
        exist_ok=True,
        workers=0,
        seed=42,
        deterministic=True,
    )


if __name__ == "__main__":
    main()
