# KDS Karar Mimarisi V1

**Tarih:** 2026-09-27  
**Durum:** Uygulama öncesi metodolojik ve teknik spesifikasyon

## Temel ilke

> Hard-rule katmanı teknik olarak değerlendirilemeyen veya açıkça uyumsuz alternatifi belirler. Çok kriterli yöntem yalnız `DEGERLENDIR` sonucuyla devam eden alternatifleri karşılaştırır.

Teknik uyumsuzluk düşük fiyat, uzun garanti, DLM, uygulama veya başka bir soft özellikle telafi edilmez. Bu belge algoritma çalıştırmaz; karar motorunun katman sınırlarını tanımlar.

## Katmanlı akış

```text
GİRDİ
  ↓
Veri doğrulama
  ↓
Teknik hard-rule / uygunluk kontrolü
  ↓
Türetilmiş kullanıcı-ihtiyaç metrikleri
  ↓
Karşılaştırılabilir aday havuzu
  ↓
Çok kriterli sıralama
  ↓
Açıklama / uyarılar
```

### 1. Girdi

`home`, `vehicle`, `user` ve gerçek wallbox katalog kaydı yüklenir. Alan anlamları `KDS_GIRDI_SOZLESMESI_V1_1.md` ile sabittir. Sözleşme gücü güvenli tesisat kapasitesi; dönem tüketimi anlık boş güç değildir.

### 2. Veri doğrulama

- Kimlik ve enum değerleri kontrol edilir.
- `null`, `Bilinmiyor` ve `Hayır` birbirine dönüştürülmez.
- Sayısal değerler sıfır veya ortalamayla tamamlanmaz.
- `kds_veri_kullanilabilir=Hayır` kayıtlar normal sıralama yoluna girmez.

### 3. Hard-rule katmanı

Sekiz V1 kuralı `KDS_HARD_RULE_SOZLUGU_V1` içinde tanımlıdır. Katman puan üretmez. HR01 kapısından sonra sonuç önceliği `ELE` → `VERI_YETERSIZ` → `DOGRULAMA_GEREKLI` → `DEGERLENDIR` biçimindedir. `ELE` yalnız açık uyumsuz kanıta dayanır.

### 4. Türetilmiş metrikler

Yalnız ön koşulları sağlanan, `DEGERLENDIR` durumundaki alternatifler için M01–M06 hesaplanabilir. Teorik etkin güç evin güvenli gücü değildir; sözleşme gücüyle minimum alınmaz.

### 5. Karşılaştırılabilir aday havuzu

- **Track A — Teknik/kullanım ihtiyacı:** `POOL_TEKNIK_27`; fiyat zorunlu değildir.
- **Track B — Ekonomik alt deney:** `POOL_FIYAT_BILINEN`; mevcut büyüklük 7. Sonuç 30 ürünlük pazarın tamamına genellenmez.

Hard-rule sonrası kalan alternatiflerin aynı kriter sütunlarında gözlenebilir olması gerekir. Eksik kriterler sayısal cezaya çevrilmez.

### 6. Çok kriterli sıralama

AHP teknik uygunluk belirlemez; seçilmiş soft kriterlerin paydaş ağırlıklarını üretebilir. TOPSIS veya baseline yöntem, yalnız aynı track, aday havuzu, kriter seti ve eksik-veri politikası altında çalıştırılır. Bu pakette ağırlık veya sıralama yoktur.

### 7. Açıklama ve uyarılar

Her sonuç; kullanılan track, hard-rule durumu, kullanılan kriterler, teorik metrikler, olumlu gerekçeler, trade-off'lar ve eksik veri uyarılarıyla birlikte döndürülür. Yöntem skoru güvenlik veya doğruluk olasılığı gibi sunulmaz.

## İzlenebilirlik

Her alternatif için şu ara çıktılar saklanmalıdır: girdi sürümleri, uygulanan kural kimlikleri, her kural sonucu/gerekçesi, metrik ön koşulları, kullanılan kriter seti, ağırlık sürümü, yöntem sürümü ve açıklama kodları. Böylece aynı girdinin aynı konfigürasyonla tekrar üretilebilirliği sağlanır.
