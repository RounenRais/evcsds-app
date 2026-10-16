# Wallbox 30 Veri Seti Raporu

**Sürüm tarihi:** 2026-09-27  
**Kapsam:** Türkiye/Avrupa pazarı için ev tipi AC Mode 3 wallbox ürünleri  
**Kayıt tanesi:** Bir satır, belirli bir marka–model–teknik varyantı temsil eder.

Bu çalışma ürün puanı, sıralaması, AHP/TOPSIS sonucu veya kurulum onayı üretmez. Mevcut 10 kayıt değerleri değiştirilmeden korunmuş, 20 gerçek varyant birincil üretici kaynakları öncelenerek eklenmiştir.

## Yönetici özeti

| Ölçüt | Sonuç |
|---|---:|
| Toplam kayıt | 30 |
| Yeni kayıt | 20 |
| Marka sayısı | 29 |
| Alan düzeyi provenans satırı | 2131 |
| Fiyatı bulunan kayıt | 7 |
| Garanti bilgisi bulunan kayıt | 8 |
| KDS çekirdeğinde kullanılabilir | 27 |
| KDS çekirdeğinde kullanılamaz | 3 |
| Çekirdek alan ortalama doluluğu | %70.6 |
| Açık kaynak çelişkisi | 1 |

Çekirdek doluluk oranında 42 V1.1 alanının tamamı kullanılmıştır. `null`, boş ve `Bilinmiyor` eksik; yapılandırılmış boş uyarı/eksik listeleri ise geçerli sonuç kabul edilmiştir.

## Yeni eklenen 20 ürün

1. Mercedes-Benz Wallbox — A0009063312, 22 kW, Type 2 shutter soket
2. Elli Charger Connect 2 — 11 kW, 4,5 m sabit Type 2 kablo, SKU 139915002C
3. MENNEKES AMTRON 4You 300 — 11 kW, Type 2 soketli varyant
4. KEBA KeContact P40 — 11 kW, 6 m sabit Type 2 kablo
5. Autel MaxiCharger AC Wallbox — AB AC W22-C5-4G-L-M-DG, 22 kW, 5 m kablo
6. Fronius Wattpilot Home 11 J — 11 kW sabit ev tipi, Type 2 soket
7. SMA EV Charger 7.4 — EVC7.4-1AC-10, 5 m sabit Type 2 kablo
8. myenergi zappi v2.1 — 7 kW tek faz, 6,5 m sabit Type 2 kablo
9. EO Charging EO Mini Pro 3 — 7,2 kW tek faz, 5 m sabit Type 2 kablo
10. Ohme Home Pro — 7,4 kW, 5 m sabit Type 2 kablo
11. Circontrol eHome5 — S, 7,4 kW tek faz, Type 2 soket
12. Wallbox Copper SB — 22 kW, Type 2 soket
13. Alfen Eve Single S-line — 904460623, 11 kW üç faz, Type 2 soket
14. Hager witty start — XEV1K07T2, 7,4 kW tek faz, Type 2S soket
15. Legrand Green'Up One — 057012, 7,4 kW, 5 m sabit Type 2 kablo
16. Bosch Power Charge 7000i — 11 kW, 5 m sabit Type 2 kablo
17. ABL eMH1 — 1W11D1, 11 kW üç faz, yaklaşık 6 m sabit Type 2 kablo
18. Delta AC MAX Basic — 22 kW, 5 m sabit Type 2 kablo
19. Charge Amps Halo — 130578, 11 kW, 7,5 m sabit Type 2 kablo
20. Compleo eBOX smart — 22 kW, Type 2 soketli duvar tipi

## Güç sınıfı dağılımı

| Sınıf | Kayıt | Oran |
|---|---:|---:|
| 22 kW | 11 | %36.7 |
| 11 kW | 10 | %33.3 |
| 7–7,4 kW | 9 | %30.0 |

7–7,4 kW sınıfına 7,0; 7,2 ve 7,4 kW nominal varyantlar birlikte dâhil edilmiştir. Mevcut pilotta 22 kW oranı %60 iken geniş veri setinde %36.7 olmuştur; gerçek ürün değerleri değiştirilmeden ağırlık azaltılmıştır.

## Faz dağılımı

| Sınıf | Kayıt | Oran |
|---|---:|---:|
| Tek ve üç faz | 14 | %46.7 |
| Yalnız tek faz | 9 | %30.0 |
| Yalnız üç faz | 5 | %16.7 |
| Kısmi/Bilinmiyor | 2 | %6.7 |

`Kısmi/Bilinmiyor`, en az bir faz desteğinin açık kaynakla doğrulanamadığı kayıtları ifade eder; bu kayıtlar başka alanlardan çıkarımla tamamlanmamıştır.

## Bağlantı tipi dağılımı

| Sınıf | Kayıt | Oran |
|---|---:|---:|
| sabit_kablolu | 17 | %56.7 |
| soketli | 13 | %43.3 |

## DLM dağılımı

| Sınıf | Kayıt | Oran |
|---|---:|---:|
| Evet | 19 | %63.3 |
| Bilinmiyor | 10 | %33.3 |
| Hayır | 1 | %3.3 |

DLM; Wi-Fi/uygulama özelliği olarak değil, ev yükünü ölçerek akımı sınırlayan kurulum özelliği olarak tutulmuştur. Harici sayaç/modül gereksinimi yalnız kaynak açıkça belirttiğinde doldurulmuştur.

## V1.1 çekirdek alan doluluk oranları

| Alan | Dolu kayıt | Doluluk |
|---|---:|---:|
| `charger_id` | 30 | %100.0 |
| `marka` | 30 | %100.0 |
| `model` | 30 | %100.0 |
| `versiyon` | 30 | %100.0 |
| `pazar` | 30 | %100.0 |
| `nominal_azami_guc_kw` | 30 | %100.0 |
| `nominal_gerilim` | 27 | %90.0 |
| `tek_faz_destegi` | 28 | %93.3 |
| `tek_faz_azami_guc_kw` | 23 | %76.7 |
| `tek_faz_azami_akim_a` | 22 | %73.3 |
| `uc_faz_destegi` | 30 | %100.0 |
| `uc_faz_azami_guc_kw` | 21 | %70.0 |
| `uc_faz_faz_basina_akim_a` | 20 | %66.7 |
| `ac_konnektor_tipi` | 30 | %100.0 |
| `ayarlanabilir_akim_destegi` | 19 | %63.3 |
| `minimum_ayarlanabilir_akim_a` | 10 | %33.3 |
| `maksimum_ayarlanabilir_akim_a` | 19 | %63.3 |
| `dinamik_yuk_yonetimi_destegi` | 20 | %66.7 |
| `harici_enerji_sayaci_gerekli_mi` | 13 | %43.3 |
| `uyumlu_yuk_yonetim_modulu` | 19 | %63.3 |
| `statik_guc_sinirlandirma_destegi` | 15 | %50.0 |
| `dc_kacak_akim_algilama_6ma` | 22 | %73.3 |
| `rdc_dd_destegi` | 9 | %30.0 |
| `dahili_rcd_tipi` | 14 | %46.7 |
| `gerekli_harici_rcd_tipi` | 5 | %16.7 |
| `ip_sinifi` | 28 | %93.3 |
| `ic_mekan_uygun` | 19 | %63.3 |
| `dis_mekan_uygun` | 20 | %66.7 |
| `baglanti_tipi` | 30 | %100.0 |
| `kablo_uzunlugu_m` | 17 | %56.7 |
| `zamanlanmis_sarj` | 10 | %33.3 |
| `enerji_olcumu` | 14 | %46.7 |
| `fiyat_tl` | 7 | %23.3 |
| `fiyat_tarihi` | 7 | %23.3 |
| `kurulum_dahil_mi` | 3 | %10.0 |
| `garanti_yil` | 8 | %26.7 |
| `dogrulama_durumu` | 30 | %100.0 |
| `veri_guven_duzeyi` | 30 | %100.0 |
| `kaynak_url` | 30 | %100.0 |
| `kds_veri_kullanilabilir` | 30 | %100.0 |
| `kds_eksik_alanlar` | 30 | %100.0 |
| `kds_veri_uyarilari` | 30 | %100.0 |

## Veri kalitesi kontrolleri

| Kontrol | Sonuç |
|---|---|
| `charger_id` benzersizliği | 30/30 benzersiz |
| Mevcut 10 kayıt | JSON değerleri birebir korundu |
| Faz desteği–güç/akım tutarlılığı | Açık çelişki yok |
| Nominal güç–faza özel güç | Nominal gücü aşan faz değeri yok |
| Minimum–maksimum akım | Ters aralık yok |
| Soketli üründe sabit kablo uzunluğu | Hata yok |
| Fiyat–fiyat tarihi | Tarihsiz fiyat yok |
| `Bilinmiyor` değerinin sessizce `Hayır` yapılması | Yapılmadı; yalnız açık olumsuz kanıtla `Hayır` kullanıldı |
| Yinelenen ürün/varyant | Bulunmadı |

KDS çekirdeğinde kullanıma kapatılan üç kayıt ve nedenleri aşağıdadır:

| Kayıt | Eksik çekirdek kanıtı |
|---|---|
| KEBA KeContact P40 | Faz akımları ve nominal gerilim exact varyant kaynağında açık sayısal alan olarak bulunamadı |
| EO Mini Pro 3 | Exact 7,2 kW sabit kablolu varyantın nominal gerilim alanı seçilen ürün kaynağında açıkça bulunamadı |
| Alfen Eve Single S-line 904460623 | Exact SKU için nominal gerilim alanı seçilen ürün/varyant kaynağında açıkça bulunamadı |

Bu kayıtların `kds_veri_kullanilabilir=Hayır` olması ürünlerin teknik olarak uygunsuz olduğu anlamına gelmez; yalnızca V1.1 çekirdek sözleşmesinin gerekli kanıtı eksik olduğundan otomatik eşleşmede kullanılmamaları gerektiğini belirtir.

## Kaynak çelişkileri

**1 çelişki:** Autel MaxiCharger AC W22-C5-4G için aynı Türkiye satıcısının ürün detay sayfasında KDV dâhil **127.980 TL**, kategori sayfasında **70.080 TL** görülmüştür. Veri setinde exact ürün detay sayfası değeri tutulmuş; ikinci değer alan provenansında ayrı satır olarak korunmuş, kayıt güveni `Orta` ve doğrulama durumu `Kısmen doğrulandı` yapılmıştır. Güncel teklif alınmadan fiyat karar girdisi olarak kullanılmamalıdır.

## En çok eksik kalan 10 alan

| Alan | Eksik kayıt | Eksik oranı |
|---|---:|---:|
| `fiyata_kdv_dahil_mi` | 29 | %96.7 |
| `kurulum_dahil_mi` | 27 | %90.0 |
| `gerekli_harici_rcd_tipi` | 25 | %83.3 |
| `dahili_asiri_akim_korumasi` | 25 | %83.3 |
| `standart_notu` | 25 | %83.3 |
| `fiyat_tl` | 23 | %76.7 |
| `fiyat_tarihi` | 23 | %76.7 |
| `coklu_sarj_cihazi_yuk_paylasimi` | 22 | %73.3 |
| `garanti_yil` | 22 | %73.3 |
| `rdc_dd_destegi` | 21 | %70.0 |

Eksiklikler hata olarak sıfırla doldurulmamıştır. `Bilinmiyor`, kaynak araştırıldığı hâlde açık kategorik kanıt bulunmadığını; `null`, sayısal/metinsel değerin bulunmadığını veya uygulanmadığını ifade eder.

## Kullanım sınırları

- Fiyatlar yalnız Türkiye kaynağında TL olarak yayımlandığında taşınmıştır; yabancı fiyatlar TL'ye çevrilmemiştir.
- DLM, RCD/RDC-DD ve faz bilgisi başka alanlardan tahmin edilmemiştir.
- `kds_veri_kullanilabilir=Evet` kurulum onayı veya belirli bir ev/araç için uygunluk değildir.
- Ürün ailesindeki opsiyonlar, seçilen exact varyanta açıkça bağlanamadığında `Bilinmiyor`/`null` bırakılmıştır.
