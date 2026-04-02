import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open("image.png")
metin = pytesseract.image_to_string(img, lang="tur+eng")

for satir in metin.split("\n"):
    if any(k in satir.lower() for k in ["demand", "çarpan", "carpan", "/"]):
        print(repr(satir))