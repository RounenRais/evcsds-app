from __future__ import annotations

import random
import shutil
from dataclasses import dataclass
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parent / "electrictiy-bills"
OUTPUT_ROOT = Path(__file__).resolve().parent / "bill_dataset_clean"
RANDOM_SEED = 42
TRAIN_RATIO = 0.8
VAL_RATIO = 0.1
TEST_RATIO = 0.1
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


@dataclass(frozen=True)
class Sample:
    image_path: Path
    label_path: Path


def polygon_line_to_bbox_line(line: str) -> str | None:
    parts = line.strip().split()
    if len(parts) < 7:
        return None

    if (len(parts) - 1) % 2 != 0:
        return None

    try:
        class_id = int(float(parts[0]))
        coords = [float(value) for value in parts[1:]]
    except ValueError:
        return None

    xs = coords[0::2]
    ys = coords[1::2]
    if not xs or not ys:
        return None

    x_min = max(0.0, min(xs))
    y_min = max(0.0, min(ys))
    x_max = min(1.0, max(xs))
    y_max = min(1.0, max(ys))

    if x_max <= x_min or y_max <= y_min:
        return None

    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0
    width = x_max - x_min
    height = y_max - y_min

    return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"


def find_image_for_label(images_dir: Path, label_stem: str) -> Path | None:
    for image_path in images_dir.iterdir():
        if image_path.is_file() and image_path.stem == label_stem and image_path.suffix.lower() in IMAGE_EXTS:
            return image_path
    return None


def collect_samples() -> list[Sample]:
    samples: list[Sample] = []
    for split_name in ("train", "test"):
        split_root = SOURCE_ROOT / split_name
        images_dir = split_root / "images"
        labels_dir = split_root / "labels"
        if not images_dir.exists() or not labels_dir.exists():
            continue

        for label_path in sorted(labels_dir.glob("*.txt")):
            if label_path.stem.startswith("result_"):
                continue

            image_path = find_image_for_label(images_dir, label_path.stem)
            if image_path is None:
                continue

            samples.append(Sample(image_path=image_path, label_path=label_path))

    return samples


def write_split(samples: list[Sample], split_name: str) -> None:
    image_out_dir = OUTPUT_ROOT / split_name / "images"
    label_out_dir = OUTPUT_ROOT / split_name / "labels"
    image_out_dir.mkdir(parents=True, exist_ok=True)
    label_out_dir.mkdir(parents=True, exist_ok=True)

    for sample in samples:
        shutil.copy2(sample.image_path, image_out_dir / sample.image_path.name)

        converted_lines: list[str] = []
        for line in sample.label_path.read_text(encoding="utf-8").splitlines():
            converted = polygon_line_to_bbox_line(line)
            if converted is not None:
                converted_lines.append(converted)

        (label_out_dir / sample.label_path.name).write_text("\n".join(converted_lines) + ("\n" if converted_lines else ""), encoding="utf-8")


def write_data_yaml() -> None:
    yaml_text = """train: train/images
val: val/images
test: test/images

nc: 1
names: ['electricity-bill']
"""
    (OUTPUT_ROOT / "data.yaml").write_text(yaml_text, encoding="utf-8")


def main() -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)

    samples = collect_samples()
    if not samples:
        raise RuntimeError("No labeled bill samples were found in train/test splits.")

    rng = random.Random(RANDOM_SEED)
    rng.shuffle(samples)

    total = len(samples)
    train_count = int(total * TRAIN_RATIO)
    val_count = int(total * VAL_RATIO)
    test_count = total - train_count - val_count

    train_samples = samples[:train_count]
    val_samples = samples[train_count:train_count + val_count]
    test_samples = samples[train_count + val_count:]

    write_split(train_samples, "train")
    write_split(val_samples, "val")
    write_split(test_samples, "test")
    write_data_yaml()

    print(f"Source labeled samples: {total}")
    print(f"Train/Val/Test: {len(train_samples)}/{len(val_samples)}/{len(test_samples)}")
    print(f"Clean dataset written to: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
