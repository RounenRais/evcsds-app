# KDS MCDM Eksik Veri Politikası V1

**Tarih:** 2026-09-27

## Temel kural

Eksik veya `Bilinmiyor` değer otomatik olarak sıfır, ortalama, medyan, en kötü ya da en iyi değerle doldurulmaz. TOPSIS karar matrisine `Bilinmiyor` stringi veya keyfi sayısal ceza sokulmaz.

Eksiklik önce kaynağına göre ayrılır:

- **Alternatif düzeyi:** Belirli wallboxın alanı eksik.
- **Senaryo düzeyi:** WLTP, bütçe, km, park süresi veya kullanıcı tercihi eksik.
- **Teknik doğrulama düzeyi:** Faz/kurulum/ürün davranışı haricî doğrulama istiyor.

## İzin verilen üç yöntem

1. Alternatif yalnız ilgili kriterli alt deneyden çıkarılır; ana teknik havuzdan “kötü ürün” diye elenmez.
2. Kriter bütün deneyde kullanılmaz; aynı aday havuzu korunur.
3. Alternatif `DOGRULAMA_GEREKLI`/`VERI_YETERSIZ` akışına ayrılır ve MCDM matrisine girmez.

Yöntem deney başlamadan seçilip raporlanmalıdır. Aynı matris içinde bazı eksiklere 0, bazılarına ortalama verilmesi yasaktır.

## Kriter bazında politika

| Kriter | V1 varsayılan politika | Yasaklanan yorum |
|---|---|---|
| C01 Günlük ihtiyaç karşılama oranı | Senaryo düzeyinde WLTP/km/park eksikse kriter o deneyde kullanılmaz; alternatif düzeyinde M02 yoksa doğrulama akışına gider | 0/ortalama atanmaz |
| C02 Teorik şarj süresi | C01 ile aynı; eksik ön koşulda kriter kullanılmaz | Sonsuz veya en kötü değer atanmaz |
| C03 Nominal kapasite kullanım oranı | M02 yoksa kriter kullanılmaz; tanısal tutulur | 0 atanmaz |
| C04 Ürün fiyatı | Track A'da kriter kullanılmaz; Track B'de fiyatı olmayan alternatif havuza alınmaz | Ortalama/medyan/TL dönüşümü yapılmaz |
| C05 Bütçe uyumu | Bütçe null ise kriter o deneyde kullanılmaz | Bütçe veya fiyat tahmin edilmez |
| C06 DLM desteği | Sabit aday havuzunda Bilinmiyor varsa kriter kullanılmaz; alternatif olarak önceden tanımlı complete-case alt deney yapılabilir | Bilinmiyor = Hayır/0 değildir |
| C07 Ayarlanabilir akım | C06 ile aynı | Bilinmiyor sayısal cezaya çevrilmez |
| C08 Garanti süresi | Genel deneyde yetersiz doluluk nedeniyle kriter kullanılmaz; yalnız garanti-dolu alt deney mümkündür | Eksik garanti 0 yıl değildir |
| C09 Zamanlanmış şarj | Kullanıcı tercihi ve veri doluluğu sağlanana kadar kriter kullanılmaz; complete-case alt deney ayrı raporlanabilir | Bilinmiyor = Hayır değildir |
| C10 Enerji ölçümü | C09 ile aynı | Bilinmiyor sayısallaştırılmaz |
| C11 Kablo/soket tercihi | Kullanıcı tercih alanı yoksa kriter kullanılmaz | Ürün tipine evrensel bonus verilmez |
| C12 Kablo uzunluğu | Kullanıcı gereksinimi yoksa kriter kullanılmaz; yalnız sabit kablolu alt kümede uygulanabilir | Soketli ürüne 0 m yazılmaz |

## Track politikası

- **Track A:** Fiyat zorunlu değildir. Eksik fiyat nedeniyle ürün çıkarılmaz; fiyat sütunu matrise konmaz.
- **Track B:** Başlangıç havuzu `POOL_FIYAT_BILINEN` ile sınırlıdır. Bu bir kalite cezası değil, ekonomik matris için gözlenebilirlik koşuludur.

Eksik-veri politikası değiştirildiğinde sonuçlar ayrı hassasiyet deneyi olarak sürümlenmeli; tek sonuç gibi birleştirilmemelidir.
