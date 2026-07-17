from pathlib import Path

import torch
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent


def main() -> None:
    model = YOLO(str(BASE_DIR / "yolo11n.pt"))
    model.train(
        data=str(BASE_DIR / "bill_scene_dataset" / "data.yaml"),
        epochs=100,
        imgsz=640,
        batch=8,
        device=0 if torch.cuda.is_available() else "cpu",
        project=str(BASE_DIR / "runs" / "detect"),
        name="electricity_bill_scene_detection_v3",
        pretrained=True,
        patience=20,
        workers=0,
        seed=20260717,
        deterministic=True,
        exist_ok=True,
    )


if __name__ == "__main__":
    main()
