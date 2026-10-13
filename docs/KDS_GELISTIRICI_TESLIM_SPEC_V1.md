# KDS Geliştirici Teslim Spesifikasyonu V1

**Tarih:** 2026-09-27  
**Amaç:** Karar motorunun katmanlarını, veri kullanım sınırlarını ve izlenebilir çıktılarını uygulama ekibine aktarmak.

## Kaynak belgeler

- `KDS_GIRDI_SOZLESMESI_V1_1.md`
- `KDS_HARD_RULE_SOZLUGU_V1.md/.xlsx`
- `KDS_KARAR_TURETILMIS_METRIKLER_V1.md`
- `KDS_KRITER_ADAYLARI_V1.xlsx`
- `KDS_MCDM_EKSIK_VERI_POLITIKASI_V1.md`
- `KDS_AHP_AGIRLIKLANDIRMA_SPEC_V1.md`
- `KDS_TOPSIS_KARAR_MATRISI_SPEC_V1.md`
- `KDS_CIKTI_ACIKLAMA_SOZLESMESI_V1.md`

## Uygulama sırası

### 1. Girdileri yükle

Ev, araç, kullanıcı ve seçili candidate pool kayıtlarını sürüm kimlikleriyle yükle. Track A için `POOL_TEKNIK_27`; ekonomik Track B için `POOL_FIYAT_BILINEN` kullanılır.

### 2. Eksik veriyi doğrula

Tip, enum, referans ve koşullu alanları denetle. `null`, `Bilinmiyor` ve `Hayır` değerlerini koru; imputasyon yapma.

### 3. Hard-rule katmanını uygula

HR01–HR08'i kimlikleri ve gerekçeleriyle çalıştır. Teknik uyumsuzluk soft kriterle telafi edilemez.

### 4. Değerlendirilemeyenleri ayır

`ELE`, `VERI_YETERSIZ` ve `DOGRULAMA_GEREKLI` alternatiflerini ayrı listelere taşı. Yalnız `DEGERLENDIR` durumundakiler soft karşılaştırmaya gider.

### 5. Günlük enerji ihtiyacını hesapla

M01'i yalnız günlük km ve WLTP tüketimi varsa üret; batarya/menzilden tahmin etme.

### 6. Teorik etkin gücü belirle

M02'yi ilgili, kanıtlı faz yolunda hesapla. Sözleşme gücüyle minimum alma. Çapraz faz kanıtı yoksa null ve doğrulama sonucu üret.

### 7. Kullanıcı ihtiyacı metriklerini üret

Ön koşulları sağlanan M03–M06'yı hesapla. M03 gerçek şarj süresi değildir; M04 kayıpları içermez; M05 otomatik benefit değildir; M06 yalnız fiyat ve bütçe doluysa vardır.

### 8. Deney/pool için kriterleri seç

Kriter seçimi track, veri doluluğu, kullanıcı tercih alanı ve eksik-veri politikasıyla uyumlu olmalıdır. Seçilen set `criterion_set_id` ile sürümlenir.

### 9. AHP ağırlıklarını al

Yalnız tamamlanmış, CR kontrolü yapılmış haricî ağırlık setini kullan. Bu pakette ağırlık yoktur. Hard-rule alanlarını AHP kriteri yapma.

### 10. TOPSIS veya baseline çalıştır

Sadece tam sayısal karar matrisi üzerinde, aynı track/havuz/kriter/ağırlık koşullarıyla çalıştır. B0 sıralama üretmez; B1/M1 ileride yöntem planına göre uygulanır.

### 11. Top-N alternatifleri üret

Top-N yalnız hard-rule sonrası kalan ve aynı karar matrisine giren alternatifler arasındadır. N, yöntem ve tie politikası koşu konfigürasyonunda belirtilir.

### 12. Açıklama ve uyarı üret

Her alternatif için hard-rule izi, kullanılan kriterler, teorik metrikler, olumlu nedenler, trade-off'lar, eksik fiyat/teknik veri uyarıları ve sürümler döndürülür. Elenen ürünlerde açık `rule_id` ve neden bulunur.

## Durum makinesi

```text
RAW
 ├─ HR01 başarısız → VERI_YETERSIZ
 ├─ açık hard-rule uyumsuzluğu → ELE
 ├─ haricî doğrulama gereken belirsizlik → DOGRULAMA_GEREKLI
 └─ bütün kapılar geçti → DEGERLENDIR → Metrik/Kriter/MCDM
```

## Zorunlu guardrail'ler

- Type 2, faz çalışabilirliği, açık kurulum yeri uyumsuzluğu ve `kds_veri_kullanilabilir` puan sütunu değildir.
- RCD/RDC-DD “varsa daha iyi” ürün bonusu değildir.
- Fiyatı olmayan ürüne fiyat atanmaz; Track A fiyat nedeniyle daraltılmaz.
- `Bilinmiyor` stringi TOPSIS matrisine veya sayısal cezaya çevrilmez.
- Yöntem skoru güvenlik/doğruluk yüzdesi olarak sunulmaz.

## Kabul kontrolleri

1. D1'de normal akış ve bütün metrik ön koşulları izlenebilir.
2. D2 M01 değerleri benchmarkla birebir uyuşur; keyfi verim yoktur.
3. D3'te temiz–bozulmuş çiftler farklı uyarı üretir, kaynak kayıt değişmez.
4. D4 hard-rule sonuçları beklenen davranışla eşleşir.
5. Aynı input + aynı sürümler aynı ara çıktıları üretir.
6. Hiçbir testte gerçek ağırlık/ürün sırası bu spesifikasyon paketinden gelmez.

## Çıktı

Çıktı alanları ve dil sınırları `KDS_CIKTI_ACIKLAMA_SOZLESMESI_V1.md` belgesinde tanımlıdır. Uygulama bu sözleşmeyi API şemasına dönüştürürken alan anlamlarını değiştirmemelidir.
