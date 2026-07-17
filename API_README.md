# EVCSDS Model API

Bu servis yalnızca elektrik sayacı ve elektrik faturası görsel analizini sunar.

## Çalıştırma

CUDA destekli PyTorch bu makinede ayrıca kuruludur. API'yi proje kökünde tek
worker ile başlatın:

```powershell
cd C:\EVCSDS
python -m pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

Servisi ve komut satırı analiz betiklerini normal giriş noktalarından başlatın;
Windows'ta CUDA DLL yükleme sırasını değiştirecek şekilde önce `paddle`, sonra
`torch` import eden özel bir başlatıcı kullanmayın.

YOLO modelleri GPU belleğinde tutulduğu için birden fazla Uvicorn worker
kullanmayın. Ölçekleme gerekiyorsa her GPU için ayrı servis örneği çalıştırın.
PaddleOCR, Windows'ta kararlılık için CPU kullanır. Aynı anda yalnızca bir analiz
çalıştırılır; diğer istekler servis içindeki semaforda sıraya alınır.

## Endpoint'ler

- `GET /health`: model ve CUDA hazır olma durumu
- `POST /analyze/meter`: sayaç tespiti, OCR ve faz çıkarımı
- `POST /analyze/bill`: fatura tespiti ve OCR
- `POST /analyze`: geriye uyumlu sayaç endpoint'i

Bütün analiz endpoint'leri `X-API-Key` header'ı ve `file` multipart alanı ister.

```powershell
$headers = @{ "X-API-Key" = "API_KEY" }
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/analyze/bill" `
  -Headers $headers `
  -Form @{ file = Get-Item "C:\faturalar\ornek.jpg" }
```

OpenAPI arayüzü servis çalışırken `http://127.0.0.1:8000/docs` adresindedir.

## Görsel sınırları

- JPEG, PNG ve WebP
- En fazla 25 MB
- En fazla 80 megapiksel
- EXIF yönü otomatik düzeltilir
- Uzun kenarda 6000 piksele kadar ayrıntı korunur
- Tespit edilen belge, OCR için örtüşmeli 1800 piksellik parçalara ayrılır
- Geçici normalize edilmiş dosya analizden sonra silinir

Fatura YOLO güveni `0.50` altındaysa yanlış kutu başarılı sayılmaz. Servis tüm
görsel OCR doğrulamasına geçer ve yanıtta `tespit_yontemi: tam_gorsel_ocr` ile
`performans_uyarisi: dusuk_guvenli_geri_donus` alanlarını döndürür. Bu güvenli
geri dönüş normal yoldan daha uzun sürebilir.

## Fatura modeliyle ilgili önemli sınır

Mevcut Roboflow fatura veri setindeki kutuların neredeyse tamamı görselin tamamını
kaplıyor. Bu nedenle yüksek test metriğine rağmen YOLO modeli, kullanıcının uzaktan
çektiği gerçek sahne fotoğraflarında faturanın sınırını güvenilir biçimde bulamıyor.
API yanlış kutuyu sonuç olarak vermemek için OCR doğrulaması ve tam-görsel geri
dönüşü uygular; fakat bu yol CPU üzerinde yavaştır.

Fatura tespitini üretim seviyesine getirmek için gerçek telefon fotoğraflarıyla yeni
bir veri seti hazırlanmalı, kutular yalnızca faturanın dört kenarını sıkıca kapsamalı
ve fatura içermeyen negatif görseller eklenmelidir. Yeni ağırlık gerçek sahne testini
geçmeden `bill_predict_and_ocr.py` içindeki etkin model yolu değiştirilmemelidir.

## API key üretimi

`/keys/generate` yalnızca sunucuda `EVCSDS_ADMIN_KEY` tanımlandığında çalışır.

```powershell
$env:EVCSDS_ADMIN_KEY = "uzun-rastgele-yonetici-anahtari"
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```
