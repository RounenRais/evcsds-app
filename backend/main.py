from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import anthropic
import base64
import io
from PIL import Image
from dotenv import load_dotenv
import os
load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API key buraya
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def goruntu_optimize_et(img_bytes):
    """Görüntüyü API'ye göndermek için optimize et"""
    img = Image.open(io.BytesIO(img_bytes))
    
    # RGB'ye çevir (PNG'lerde alpha kanalı olabilir)
    if img.mode != "RGB":
        img = img.convert("RGB")
    
    # Çok büyükse küçült (API limiti)
    max_boyut = 1568
    if max(img.size) > max_boyut:
        img.thumbnail((max_boyut, max_boyut))
    
    # JPEG olarak kaydet
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return buffer.getvalue()

def fatura_analiz_claude(img_bytes):
    """Claude ile faturayı analiz et"""
    
    # Base64'e çevir
    img_base64 = base64.standard_b64encode(img_bytes).decode("utf-8")
    
    # Claude'a gönder
    mesaj = client.messages.create(
model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": img_base64,
                        },
                    },
                    {
                        "type": "text",
                      "text": """Bu bir Türkiye elektrik faturasıdır. 
Lütfen aşağıdaki bilgileri bul ve SADECE JSON formatında döndür, başka hiçbir şey yazma:

{
    "sozlesme_gucu": <kW cinsinden sayı, bulunamazsa null>,
    "tuketici_grubu": <"mesken" veya "ticarethane" veya null>,
    "aciklama": <kısa açıklama>
}

ÖNEMLİ KURALLAR:
- "Fatura Ort. Tüketim (kWh/gün)" değerini ALMA, bu sözleşme gücü değildir!
- "Ödenecek Tutar" değerini ALMA, bu paradır!
- Sadece şu ifadeleri ara:
  * "Sözleşme Gücü", "Anlaşma Gücü", "Bağlantı Gücü", "Abone Gücü"
  * "Çarpan/Demand/Anl.Gücü" → sondaki sayıyı al (örn: 1.000/3.000 → 3.0 kW)
  * "Kurulu Güç/Sözleşme Gücü" → sondaki sayıyı al (örn: 11.260/6.750 → 6.75 kW)
- Değer 1000'den büyükse 1000'e böl (örn: 7600 → 7.6 kW)
- Tüketici grubu için: "Mesken" veya "Ticarethane" geçiyor mu bak."""
                    }
                ],
            }
        ],
    )
    
    # Cevabı parse et
    cevap = mesaj.content[0].text.strip()
    
    # JSON temizle
    import json
    if "```json" in cevap:
        cevap = cevap.split("```json")[1].split("```")[0].strip()
    elif "```" in cevap:
        cevap = cevap.split("```")[1].split("```")[0].strip()
    
    return json.loads(cevap)

@app.post("/fatura-analiz")
async def fatura_analiz(file: UploadFile = File(...)):
    # Dosya boyutu kontrolü (max 10MB)
    icerik = await file.read()
    if len(icerik) > 10 * 1024 * 1024:
        return {
            "basarili": False,
            "sozlesme_gucu": None,
            "tuketici_grubu": None,
            "mesaj": "Dosya çok büyük, maksimum 10MB yükleyebilirsiniz."
        }
    
    # Görüntüyü optimize et
    try:
        optimize_img = goruntu_optimize_et(icerik)
    except Exception:
        return {
            "basarili": False,
            "sozlesme_gucu": None,
            "tuketici_grubu": None,
            "mesaj": "Görüntü işlenemedi, lütfen geçerli bir fotoğraf yükleyin."
        }
    
    # Claude ile analiz et
    try:
        sonuc = fatura_analiz_claude(optimize_img)
        
        guc = sonuc.get("sozlesme_gucu")
        grup = sonuc.get("tuketici_grubu")
        aciklama = sonuc.get("aciklama", "")
        
        if guc:
            return {
                "basarili": True,
                "sozlesme_gucu": guc,
                "tuketici_grubu": grup,
                "mesaj": f"Sözleşme gücü tespit edildi: {guc} kW",
                "aciklama": aciklama
            }
        else:
            return {
                "basarili": False,
                "sozlesme_gucu": None,
                "tuketici_grubu": grup,
                "mesaj": "Sözleşme gücü faturada bulunamadı, lütfen manuel girin.",
                "aciklama": aciklama
            }
    
    except Exception as e:
        return {
            "basarili": False,
            "sozlesme_gucu": None,
            "tuketici_grubu": None,
            "mesaj": "Analiz sırasında hata oluştu, lütfen tekrar deneyin."
        }

@app.get("/")
def root():
    return {"mesaj": "EV Şarj Karar Destek API çalışıyor!"}