# EVCSDS — Ev tipi AC şarj karar destek sistemi

Elektrik sayacı ve faturanızdan evin elektrik altyapısını okur, aracınızı
sorar ve 30 wallbox'ı teknik kurallara göre dört gruba ayırır.

Sistem **sıralama veya puan üretmez** ve **kurulum onayı vermez**. Ürünleri
ayıklar, gerekçesini yazar, kararı kullanıcıya bırakır.

## Nereden geldi

Üç ayrı branch'te gelişen iki parça burada birleştirildi:

| Kaynak | Ne getirdi |
|---|---|
| `yolo` | YOLO + PaddleOCR görsel analizi → `backend/vision/` |
| `kds` | Karar motoru, araç/wallbox katalogları → `backend/kds_engine/`, `backend/data/` |
| `main` | Next.js iskeleti → `frontend/` |

`backend/kds_engine/` **değiştirilmeden** taşındı. Taşımanın bir şeyi bozmadığı
85 senaryoluk benchmark'ın aynı sonucu vermesiyle doğrulanır.

## Klasörler

```
backend/
  main.py          Birleşik FastAPI servisi
  vision/          Sayaç ve fatura görsellerinden alan çıkarma
  kds_engine/      Karar motoru (HR01–HR08 kuralları, M01–M06 metrikleri)
  catalog.py       Araç/wallbox kataloğu ve arama
  recommend.py     Görsel çıktısı ile motor arasındaki köprü
  data/            100 araç, 30 wallbox, 15 ev profili, 85 senaryo
  models/          YOLO ağırlıkları (sayaç + fatura)
frontend/          Next.js arayüzü — 4 adımlı akış
tests/             Birim ve entegrasyon testleri
docs/              Kural sözlükleri, metrik tanımları, veri raporları
```

## Kurulum

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp keys.example.json keys.json
uvicorn main:app --port 8000
```

Bu haliyle katalog ve öneri uçları çalışır. **Görsel analiz için ek kurulum
gerekir** (birkaç GB, CUDA sürümüne bağlı):

```bash
pip install -r requirements-vision.txt
```

Görsel katmanı bilerek tembel yüklenir: kurulu değilse `/analyze/*` uçları
503 döner, diğer her şey çalışmaya devam eder.

> YOLO modelleri GPU belleğinde tutulduğu için **tek worker** ile çalıştırın.
> Ölçekleme gerekiyorsa her GPU için ayrı servis örneği açın.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local     # EVCSDS_API_KEY'i doldurun
npm run dev
```

### API anahtarı

Görsel analiz uçları `X-API-Key` ister. Anahtar üretmek için:

```bash
EVCSDS_ADMIN_KEY="uzun-rastgele-bir-dize" uvicorn main:app --port 8000
curl -X POST "http://localhost:8000/keys/generate?kullanici_adi=ad" \
     -H "X-Admin-Key: uzun-rastgele-bir-dize"
```

Anahtar `backend/keys.json` dosyasına yazılır ve bu dosya `.gitignore`
altındadır. **Anahtar tarayıcıya hiçbir zaman gönderilmez**: arayüz görsel
analizi `frontend/app/api/analiz-ev` sunucu vekili üzerinden çağırır.

## Uçlar

| Uç | Anahtar | Ne yapar |
|---|---|---|
| `GET /health` | — | Katalog ve model ağırlıkları hazır mı |
| `GET /catalog/vehicles?q=` | — | Araç araması (Türkçe duyarlı) |
| `GET /catalog/wallboxes` | — | 30 wallbox |
| `POST /recommend` | — | Dört aday listesi + metrikler |
| `POST /analyze/meter` | ✓ | Sayaçtan faz |
| `POST /analyze/bill` | ✓ | Faturadan alanlar |
| `POST /analyze/home` | ✓ | İkisinden KDS ev girdisi |

`/recommend` gövdesinde **`kullanici_onayladi: true`** zorunludur. Görsel
analizden gelen hiçbir değer, kullanıcı doğrulamadan karar verisi sayılmaz;
`/analyze/home` zaten `kdsye_dogrudan_aktarilabilir: false` döndürür.

## Testler

```bash
# 85 senaryoluk motor benchmark'ı — harici paket gerektirmez
cd backend && python -B -m kds_engine.run_benchmark

# Birim + entegrasyon testleri
pip install pytest
cd .. && python -m pytest tests/ -q
```

Benchmark'ın beklenen çıktısı: 85 senaryo, 2.153 alternatif değerlendirmesi,
2.683/2.683 kontrol, 19/19 beklenen statü eşleşmesi.

## Bilinen sınırlar

- **Fatura tespiti üretim seviyesinde değil.** Eğitim veri setindeki kutuların
  neredeyse tamamı tam kare olduğundan model, uzaktan çekilmiş gerçek sahne
  fotoğraflarında faturanın sınırını güvenilir bulamıyor. Bulamayınca tüm
  görsel parçalara ayrılıp OCR'dan geçer; bu yol işlemcide yavaştır.
  Ayrıntı: `docs/gorsel/MODEL_DURUMU.md`.
- **100 aracın 24'ünde WLTP tüketim verisi yok** (tüm TOGG'lar, Tesla Model 3
  ve Model Y dahil). Bu araçlarda M01, M03 ve M04 hesaplanmaz. Sistem tahmin
  üretmez; arayüz kullanıcıdan tüketimi girmesini ister.
- **30 wallbox'ın 23'ünde fiyat kaydı yok.** Fiyatı bilinmeyen ürün elenmez,
  yalnız bütçe karşılaştırmasına giremez.
- Araç ve wallbox görselleri yoktur; arayüz marka logosu veya harf monogramı
  gösterir. Logolar `simple-icons` paketinden `npm run logolar` ile üretilir.

## Tasarım

Arayüz tasarımının tıklanabilir prototipi ayrı bir belgede tutulur. Durum
renkleri (uygun / doğrulanmalı / elenen / veri yetersiz) renk körlüğü
ayrımı için doğrulanmıştır ve hiçbir yerde renk tek başına anlam taşımaz:
her durumun ikonu ve yazısı vardır.
