# KDS Geliştirici Teslim Paketi V1

Bu paket, ev tipi AC wallbox karar destek motorunu geliştirecek ekip üyesi için hazırlanmıştır.

## Nereden başlanmalı?

1. `00_BASLANGIC/KDS_GELISTIRICI_TESLIM_SPEC_V1.md`
2. `00_BASLANGIC/KDS_KARAR_MIMARISI_V1.md`
3. `01_KURALLAR_VE_SOZLESMELER/KDS_HARD_RULE_SOZLUGU_V1.md`
4. `01_KURALLAR_VE_SOZLESMELER/KDS_KARAR_TURETILMIS_METRIKLER_V1.md`
5. `01_KURALLAR_VE_SOZLESMELER/KDS_MCDM_EKSIK_VERI_POLITIKASI_V1.md`
6. `04_MCDM_METODOLOJI/KDS_TOPSIS_KARAR_MATRISI_SPEC_V1.md`
7. `03_BENCHMARK_VE_TESTLER/KDS_BENCHMARK_D1_D4.json`

## Geliştirilecek akış

`Girdi -> veri doğrulama -> hard rules -> türetilmiş metrikler -> aday havuzu -> ağırlık seti -> TOPSIS/baseline -> Top-N -> açıklama/uyarı`

Hard-rule sonucu `ELE`, `VERI_YETERSIZ` veya `DOGRULAMA_GEREKLI` olan alternatifler soft sıralamaya sokulmamalıdır. Yalnız `DEGERLENDIR` durumundaki alternatifler MCDM matrisine gider.

## Ana veri setleri

- `ARAC_KDS_CEKIRDEK_100`: 100 gerçek araç varyantı.
- `WALLBOX_KDS_CEKIRDEK_30_V1_1`: 30 gerçek wallbox kaydı; normal teknik havuz 27 üründür.
- `KDS_ADAY_HAVUZLARI.json`: Track ve deney havuzları.
- `KDS_BENCHMARK_D1_D4`: toplam 85 kontrollü senaryo.

## Deneyler

- D1: temiz/tam veri, temel karar akışı.
- D2: günlük enerji ihtiyacı ve park süresi stres senaryoları.
- D3: eksik/belirsiz veri davranışı.
- D4: teknik sınır ve hard-rule davranışı.

## AHP/TOPSIS

AHP yalnız soft kriter ağırlıklarını üretmek için kullanılacaktır. Bu pakette gerçek ağırlık yoktur. Ağırlıklar kod içine hard-code edilmemeli; haricî/sürümlü `weight_set` olarak alınmalıdır.

TOPSIS yalnız hard-rule sonrası kalan, aynı kriterleri eksiksiz sayısal olarak taşıyan alternatifler üzerinde çalıştırılmalıdır. `Bilinmiyor` veya `null` değerlere keyfî ceza/imputasyon yapılmamalıdır.

## Track'ler

- Track A: `POOL_TEKNIK_27`. Fiyat zorunlu değildir.
- Track B: `POOL_FIYAT_BILINEN`. Mevcut durumda 7 ürün; fiyat/bütçe deneyleri bu alt kümede yapılır.

## Kabul kriterleri

- D1: normal akış ve metrik ön koşulları izlenebilir olmalı.
- D2: günlük enerji ihtiyacı benchmark değerleriyle birebir aynı olmalı.
- D3: temiz/bozulmuş çiftler farklı ve doğru uyarı üretmeli; kaynak kayıtlar değişmemeli.
- D4: hard-rule sonuçları beklenen davranışla eşleşmeli.
- Aynı input + aynı konfigürasyon aynı ara çıktıyı üretmeli.
- TOPSIS skoru güvenlik/doğruluk yüzdesi gibi yorumlanmamalı.

## Önemli kapsam sınırı

Sistem ürün seçimine yönelik karar desteğidir. `sozlesme_gucu_kw`, sayaç azami akımı veya geçmiş tüketim doğrudan güvenli tesisat gücü olarak kullanılmamalıdır.

## Paket notu

Ana spesifikasyon `KDS_GIRDI_SOZLESMESI_V1_1.md` dosyasına referans veriyor; bu dosyanın V1.1 sürümü bu sohbette yüklenmiş dosyalar arasında mevcut değildi. Bu nedenle `05_REFERANS_VE_PROVENANS/` klasörüne yalnız önceki `KDS_GIRDI_SOZLESMESI_V1_REFERANS.md` kopyası konuldu. Eğer ekipte V1.1 dosyası mevcutsa, teslimden önce pakete eklenmesi tercih edilir. Uygulamada V1.1 karar mimarisi, hard rule ve metrik belgeleri önceliklidir.

## Dosya klasörleri

- `00_BASLANGIC`: ana geliştirici dokümanları.
- `01_KURALLAR_VE_SOZLESMELER`: hard rules, metrikler, eksik veri ve çıktı sözleşmesi.
- `02_CEKIRDEK_VERILER`: araç, wallbox, profil ve aday havuzları.
- `03_BENCHMARK_VE_TESTLER`: D1-D4 ve test dosyaları.
- `04_MCDM_METODOLOJI`: kriter, AHP, TOPSIS ve yöntem karşılaştırma belgeleri.
- `05_REFERANS_VE_PROVENANS`: veri toplama/kalite/provenans belgeleri.
