from ultralytics import YOLO


def main():
    model = YOLO("yolo11n.pt")

    model.train(
        data="data.yaml",
        epochs=100,        # daha fazla veri var, artırdık
        imgsz=640,
        batch=8,
        device='cpu',
        project="runs",
        name="electric_meter_detection3",
        pretrained=True,
        verbose=True,
        augment=True,
        patience=20,       # 20 epoch iyileşme olmazsa durur
        exist_ok=False,    # aynı isimde klasör varsa hata verir, dikkat
    )


if __name__ == "__main__":
    main()