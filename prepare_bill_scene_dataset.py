from __future__ import annotations

import random
import shutil
from pathlib import Path

import cv2
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "new_electric_bills_model"
OUTPUT_DIR = BASE_DIR / "bill_scene_dataset"
BACKGROUND_DIRS = [BASE_DIR / "sayac_photos", BASE_DIR / "test_images"]
IMAGE_SIZE = 640
SEED = 20260717
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _background_paths() -> list[Path]:
    return [
        path
        for folder in BACKGROUND_DIRS
        if folder.is_dir()
        for path in folder.iterdir()
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
        and not path.name.startswith("result_")
    ]


def _cover_resize(image: np.ndarray, size: int) -> np.ndarray:
    h, w = image.shape[:2]
    scale = max(size / w, size / h)
    resized = cv2.resize(
        image,
        (max(size, round(w * scale)), max(size, round(h * scale))),
        interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR,
    )
    h, w = resized.shape[:2]
    x = (w - size) // 2
    y = (h - size) // 2
    return resized[y : y + size, x : x + size].copy()


def _procedural_background(rng: random.Random) -> np.ndarray:
    base = np.empty((IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.float32)
    color = np.array([rng.randint(35, 225) for _ in range(3)], dtype=np.float32)
    base[:] = color
    noise = np.random.default_rng(rng.randrange(2**32)).normal(
        0, rng.uniform(5, 28), base.shape
    )
    base = np.clip(base + noise, 0, 255).astype(np.uint8)
    if rng.random() < 0.7:
        for _ in range(rng.randint(5, 20)):
            p1 = (rng.randrange(IMAGE_SIZE), rng.randrange(IMAGE_SIZE))
            p2 = (rng.randrange(IMAGE_SIZE), rng.randrange(IMAGE_SIZE))
            line_color = tuple(rng.randint(20, 235) for _ in range(3))
            cv2.line(base, p1, p2, line_color, rng.randint(1, 5))
    return cv2.GaussianBlur(base, (5, 5), 0)


def _background(rng: random.Random, paths: list[Path]) -> np.ndarray:
    if paths and rng.random() < 0.75:
        image = cv2.imread(str(rng.choice(paths)))
        if image is not None:
            return _cover_resize(image, IMAGE_SIZE)
    return _procedural_background(rng)


def _bill_scene(
    bill: np.ndarray, background: np.ndarray, rng: random.Random
) -> tuple[np.ndarray, tuple[float, float, float, float]]:
    target_h = rng.randint(round(IMAGE_SIZE * 0.55), round(IMAGE_SIZE * 0.94))
    aspect = rng.uniform(0.24, 0.56)
    target_w = max(80, min(round(target_h * aspect), round(IMAGE_SIZE * 0.58)))
    bill = cv2.resize(bill, (target_w, target_h), interpolation=cv2.INTER_AREA)

    x = rng.randint(5, IMAGE_SIZE - target_w - 5)
    y = rng.randint(5, IMAGE_SIZE - target_h - 5)
    overlay = np.zeros_like(background)
    mask = np.zeros((IMAGE_SIZE, IMAGE_SIZE), dtype=np.uint8)
    overlay[y : y + target_h, x : x + target_w] = bill
    mask[y : y + target_h, x : x + target_w] = 255

    angle = rng.uniform(-10, 10)
    center = (x + target_w / 2, y + target_h / 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    overlay = cv2.warpAffine(
        overlay, matrix, (IMAGE_SIZE, IMAGE_SIZE), flags=cv2.INTER_LINEAR
    )
    mask = cv2.warpAffine(
        mask, matrix, (IMAGE_SIZE, IMAGE_SIZE), flags=cv2.INTER_NEAREST
    )

    alpha = (mask.astype(np.float32) / 255.0)[..., None]
    scene = (overlay * alpha + background * (1 - alpha)).astype(np.uint8)
    ys, xs = np.where(mask > 0)
    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())
    cx = ((x1 + x2) / 2) / IMAGE_SIZE
    cy = ((y1 + y2) / 2) / IMAGE_SIZE
    width = (x2 - x1 + 1) / IMAGE_SIZE
    height = (y2 - y1 + 1) / IMAGE_SIZE
    return scene, (cx, cy, width, height)


def _write_split(split: str, rng: random.Random, backgrounds: list[Path]) -> None:
    image_source = SOURCE_DIR / split / "images"
    image_output = OUTPUT_DIR / split / "images"
    label_output = OUTPUT_DIR / split / "labels"
    image_output.mkdir(parents=True, exist_ok=True)
    label_output.mkdir(parents=True, exist_ok=True)

    sources = sorted(
        path
        for path in image_source.iterdir()
        if path.suffix.lower() in IMAGE_EXTENSIONS
    )
    for index, source in enumerate(sources):
        bill = cv2.imread(str(source))
        if bill is None:
            continue
        scene, box = _bill_scene(bill, _background(rng, backgrounds), rng)
        name = f"bill_scene_{index:04d}"
        cv2.imwrite(str(image_output / f"{name}.jpg"), scene)
        (label_output / f"{name}.txt").write_text(
            "0 " + " ".join(f"{value:.6f}" for value in box) + "\n",
            encoding="utf-8",
        )

    negative_count = max(5, round(len(sources) * 0.10))
    for index in range(negative_count):
        name = f"negative_{index:04d}"
        cv2.imwrite(
            str(image_output / f"{name}.jpg"), _background(rng, backgrounds)
        )
        (label_output / f"{name}.txt").write_text("", encoding="utf-8")


def main() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    rng = random.Random(SEED)
    backgrounds = _background_paths()
    for split in ("train", "valid", "test"):
        _write_split(split, rng, backgrounds)

    (OUTPUT_DIR / "data.yaml").write_text(
        f"path: {OUTPUT_DIR.as_posix()}\n"
        "train: train/images\n"
        "val: valid/images\n"
        "test: test/images\n\n"
        "nc: 1\n"
        "names: ['electricity-bill']\n",
        encoding="utf-8",
    )
    print(f"Scene dataset created: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
