from pathlib import Path
from icrawler.builtin import BingImageCrawler
import os

# Kaydedilecek klasör
SAVE_DIR = Path(r"C:\EASIOS\sayac_photos")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# Türkiye odaklı sorgular
QUERIES = [
    "elektrik sayacı",
    "elektrik sayacı pano",
    "apartman elektrik sayacı panosu",
    "bina elektrik sayacı panosu",
    "monofaz elektrik sayacı",
    "trifaz elektrik sayacı",
    "köhler elektrik sayacı",
    "luna elektrik sayacı",
    "tedaş elektrik sayacı",
    "tedaş uyumlu elektrik sayacı",
]

# Her sorgudan kaç görsel indirilsin
MAX_NUM_PER_QUERY = 20


def get_next_index(save_dir: Path) -> int:
    nums = []
    for f in save_dir.iterdir():
        if f.is_file() and f.stem.startswith("sayac"):
            suffix = f.stem.replace("sayac", "")
            if suffix.isdigit():
                nums.append(int(suffix))
    return max(nums, default=0) + 1


def rename_downloaded_files(save_dir: Path) -> None:
    """
    icrawler dosyaları varsayılan isimlerle indirir.
    Bu fonksiyon onları sayac001.jpg, sayac002.jpg ... diye yeniden adlandırır.
    """
    files = sorted([f for f in save_dir.iterdir() if f.is_file()])
    next_idx = get_next_index(save_dir)

    for f in files:
        # Zaten sayacXXX ise geç
        if f.stem.startswith("sayac"):
            continue

        ext = f.suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
            # uzantısı garipse jpg yapma, geç
            continue

        new_name = f"sayac{next_idx:03d}{ext if ext else '.jpg'}"
        new_path = save_dir / new_name

        # çakışma varsa artır
        while new_path.exists():
            next_idx += 1
            new_name = f"sayac{next_idx:03d}{ext if ext else '.jpg'}"
            new_path = save_dir / new_name

        os.rename(f, new_path)
        print(f"Yeniden adlandırıldı: {f.name} -> {new_name}")
        next_idx += 1


def main():
    print(f"Kayıt klasörü: {SAVE_DIR}")

    for query in QUERIES:
        print(f"\nAranıyor: {query}")

        crawler = BingImageCrawler(
            storage={"root_dir": str(SAVE_DIR)}
        )

        try:
            crawler.crawl(
                keyword=query,
                max_num=MAX_NUM_PER_QUERY,
                min_size=(300, 300)
            )
        except Exception as e:
            print(f"Hata: {e}")

        rename_downloaded_files(SAVE_DIR)

    print("\nİndirme tamamlandı.")


if __name__ == "__main__":
    main()