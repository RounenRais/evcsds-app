# Wallbox Pilot Veri Kalitesi Raporu

**Değerlendirme tarihi:** 2026-09-27

## 1. Veri seti ve kayıt tanesi

Pilot veri seti, her biri tek bir marka + model + güç + bağlantı + pazar varyantını temsil eden **10 kayıt** ve mevcut şemadaki **71 alan** içerir. DC hızlı şarj ürünleri ve karar puanları kapsam dışındadır.

Eksiklik gösterimi şu şekilde uygulanmıştır: araştırılan kategorik alanda açık beyan yoksa `Bilinmiyor`; sayısal/metinsel değer açıklanmamışsa `null`; açık olumlu/olumsuz kanıt varsa `Evet/Hayır`.

## 2. Yapılan kontroller

- `charger_id` benzersizliği ve kayıt sayısı.
- 71 alanın tamamının her JSON kaydında aynı sırada bulunması.
- Tek/üç faz desteği ile faza özel güç ve akım alanlarının tutarlılığı.
- Nominal azami güç ile faza özel üst sınırların uyumu.
- 230 V tek faz ve 400 V üç faz için güç-akım çiftlerinin yaklaşık fiziksel tutarlılığı (±%15 tolerans).
- Minimum/maksimum sıcaklık sırası, fiyat-tarih birlikteliği ve URL biçimi.
- Her ürün-alan çifti için alan düzeyi kaynak kaydı.
- Kaynaklar arası açık birim/özellik çatışmaları.

## 3. Sonuç özeti

- Çekirdek teknik alanlarda ortalama doluluk: **%75.7**.
- En az iki farklı URL ile doğrulanan ürün: **10/10**.
- Fiyatı TL olarak ve tarihli kaydedilen ürün: **6/10**.
- Alan düzeyi provenans satırı: **710 / 710**.
- Açık kaynak çatışması: **1**.
- Otomatik tutarlılık kontrollerinde faz/güç/akım, sıcaklık, kimlik veya fiyat-tarih ilişkisi için kritik/yüksek hata bulunmadı.

## 4. En çok eksik kalan beş alan

| Alan | Eksik/Bilinmiyor | Doluluk | Başlıca neden |
|---|---:|---:|---|
| `fiyata_kdv_dahil_mi` | 10/10 | %0.0 | Üretici kaynaklarında açık ve varyanta özgü beyan sınırlı. |
| `ethernet` | 8/10 | %20.0 | Üreticiler çoğu konut ürününde kablolu haberleşmeyi açıkça belirtmiyor. |
| `gerekli_harici_rcd_tipi` | 8/10 | %20.0 | Koruma düzeni yerel kurala veya exact donanım varyantına bırakılıyor. |
| `dahili_asiri_akim_korumasi` | 7/10 | %30.0 | Üretici kaynaklarında açık ve varyanta özgü beyan sınırlı. |
| `kurulum_dahil_mi` | 7/10 | %30.0 | Üretici kaynaklarında açık ve varyanta özgü beyan sınırlı. |

## 5. Alan bazında doluluk

`Bilinmiyor` ve `null` kullanılabilir teknik değer olarak sayılmamıştır.

| Alan | Dolu | Bilinmiyor | null/boş | Doluluk |
|---|---:|---:|---:|---:|
| `charger_id` | 10 | 0 | 0 | %100.0 |
| `marka` | 10 | 0 | 0 | %100.0 |
| `model` | 10 | 0 | 0 | %100.0 |
| `versiyon` | 10 | 0 | 0 | %100.0 |
| `pazar` | 10 | 0 | 0 | %100.0 |
| `urun_durumu` | 10 | 0 | 0 | %100.0 |
| `kaynak_tipi` | 10 | 0 | 0 | %100.0 |
| `kaynak_basligi` | 10 | 0 | 0 | %100.0 |
| `kaynak_url` | 10 | 0 | 0 | %100.0 |
| `erisim_tarihi` | 10 | 0 | 0 | %100.0 |
| `dogrulama_durumu` | 10 | 0 | 0 | %100.0 |
| `veri_guven_duzeyi` | 10 | 0 | 0 | %100.0 |
| `kaynak_notu` | 10 | 0 | 0 | %100.0 |
| `sarj_modu` | 10 | 0 | 0 | %100.0 |
| `nominal_azami_guc_kw` | 10 | 0 | 0 | %100.0 |
| `tek_faz_destegi` | 9 | 1 | 0 | %90.0 |
| `tek_faz_azami_guc_kw` | 7 | 0 | 3 | %70.0 |
| `tek_faz_azami_akim_a` | 7 | 0 | 3 | %70.0 |
| `uc_faz_destegi` | 10 | 0 | 0 | %100.0 |
| `uc_faz_azami_guc_kw` | 8 | 0 | 2 | %80.0 |
| `uc_faz_faz_basina_akim_a` | 8 | 0 | 2 | %80.0 |
| `ayarlanabilir_akim_destegi` | 8 | 2 | 0 | %80.0 |
| `minimum_ayarlanabilir_akim_a` | 4 | 0 | 6 | %40.0 |
| `maksimum_ayarlanabilir_akim_a` | 8 | 0 | 2 | %80.0 |
| `nominal_gerilim` | 10 | 0 | 0 | %100.0 |
| `frekans_hz` | 10 | 0 | 0 | %100.0 |
| `ac_konnektor_tipi` | 10 | 0 | 0 | %100.0 |
| `baglanti_tipi` | 10 | 0 | 0 | %100.0 |
| `kablo_uzunlugu_m` | 5 | 0 | 5 | %50.0 |
| `dinamik_yuk_yonetimi_destegi` | 7 | 3 | 0 | %70.0 |
| `dinamik_yuk_yonetimi_dahili_mi` | 7 | 3 | 0 | %70.0 |
| `harici_enerji_sayaci_gerekli_mi` | 7 | 3 | 0 | %70.0 |
| `uyumlu_yuk_yonetim_modulu` | 7 | 0 | 3 | %70.0 |
| `statik_guc_sinirlandirma_destegi` | 8 | 2 | 0 | %80.0 |
| `coklu_sarj_cihazi_yuk_paylasimi` | 6 | 4 | 0 | %60.0 |
| `dc_kacak_akim_algilama_6ma` | 7 | 3 | 0 | %70.0 |
| `rdc_dd_destegi` | 4 | 6 | 0 | %40.0 |
| `dahili_rcd_tipi` | 5 | 5 | 0 | %50.0 |
| `gerekli_harici_rcd_tipi` | 2 | 8 | 0 | %20.0 |
| `dahili_asiri_akim_korumasi` | 3 | 7 | 0 | %30.0 |
| `koruma_notu` | 10 | 0 | 0 | %100.0 |
| `iec_61851_uyumu` | 9 | 1 | 0 | %90.0 |
| `iec_62196_uyumu` | 7 | 3 | 0 | %70.0 |
| `iec_62955_uyumu` | 4 | 6 | 0 | %40.0 |
| `ce_beyani` | 6 | 4 | 0 | %60.0 |
| `standart_notu` | 5 | 0 | 5 | %50.0 |
| `ip_sinifi` | 10 | 0 | 0 | %100.0 |
| `ik_sinifi` | 7 | 3 | 0 | %70.0 |
| `ic_mekan_uygun` | 10 | 0 | 0 | %100.0 |
| `dis_mekan_uygun` | 10 | 0 | 0 | %100.0 |
| `calisma_sicakligi_min_c` | 10 | 0 | 0 | %100.0 |
| `calisma_sicakligi_max_c` | 10 | 0 | 0 | %100.0 |
| `wifi` | 8 | 2 | 0 | %80.0 |
| `ethernet` | 2 | 8 | 0 | %20.0 |
| `bluetooth` | 4 | 6 | 0 | %40.0 |
| `mobil_uygulama` | 7 | 3 | 0 | %70.0 |
| `zamanlanmis_sarj` | 7 | 3 | 0 | %70.0 |
| `rfid` | 6 | 4 | 0 | %60.0 |
| `ocpp_destegi` | 6 | 4 | 0 | %60.0 |
| `ocpp_surumu` | 6 | 4 | 0 | %60.0 |
| `uzaktan_izleme` | 7 | 3 | 0 | %70.0 |
| `enerji_olcumu` | 8 | 2 | 0 | %80.0 |
| `solar_sarj_destegi` | 4 | 6 | 0 | %40.0 |
| `fiyat_tl` | 6 | 0 | 4 | %60.0 |
| `fiyat_tarihi` | 6 | 0 | 4 | %60.0 |
| `fiyata_kdv_dahil_mi` | 0 | 10 | 0 | %0.0 |
| `kurulum_dahil_mi` | 3 | 7 | 0 | %30.0 |
| `garanti_yil` | 7 | 0 | 3 | %70.0 |
| `teknik_not` | 10 | 0 | 0 | %100.0 |
| `kurulum_notu` | 10 | 0 | 0 | %100.0 |
| `varyant_notu` | 10 | 0 | 0 | %100.0 |

## 6. Tutarlılık ve çatışma bulguları

| Önem | Kontrol | Bulgular ve etki |
|---|---|---|
| Orta | Kaynaklar arası birim çatışması | ARCELIK_AR_AW32_RFID_7_4_TR: ürün sayfası güç hücresini 7,4 kWh yazar; üretici teknik kataloğu ve model adı 7,4 kW olarak doğrular. Veri setinde kW kullanıldı. |
| Düşük | Faz/güç/akım kontrolü | 10 kayıtta faz desteği ile faza özel alanlar arasında çelişki bulunmadı; güç-akım çiftleri yaklaşık elektriksel sınırlar içindedir. |
| Düşük | Kimlik ve şema | 10 charger_id benzersizdir; tüm JSON nesneleri aynı 71 anahtarı içerir. |
| Düşük | Eksik değer sözlüğü | Boş string kullanılmadı; kategorik eksiklerde Bilinmiyor, sayısal/metinsel eksiklerde null kullanıldı. |

Arçelik çatışmasının etkisi sınırlıdır: üretici ürün sayfasındaki `7.4 kWh` yazımı enerji birimi olarak hatalıdır; aynı üreticinin teknik kataloğu, model adı ve altyapı dokümanı `7,4 kW` değerini doğruladığı için kayıt `7.4 kW` olarak tutulmuştur. Bu düzeltme alan-kaynak dosyasında açıkça belgelenmiştir.

## 7. Fiyat verisi

| Ürün | Fiyat (TL) | Tarih | KDV | Kurulum | Kaynak sınıfı |
|---|---:|---|---|---|---|
| Tesla Wall Connector | 29.670 | 2026-09-27 | Bilinmiyor | Hayır | Üretici Türkiye sitesi |
| Vestel EVC04 | 28.499 | 2026-09-27 | Bilinmiyor | Evet | Üretici Türkiye sitesi |
| ABB Terra AC | 65.000 | 2026-09-27 | Bilinmiyor | Bilinmiyor | Yetkili distribütör |
| Wallbox Pulsar Plus | 33.064 | 2026-09-27 | Bilinmiyor | Bilinmiyor | Güvenilir ikincil kaynak |
| Schneider Electric Schneider Charge | 39.600 | 2026-09-27 | Bilinmiyor | Bilinmiyor | Güvenilir ikincil kaynak |
| Arçelik by WAT AR AW 32 RFID | 24.499 | 2026-09-27 | Bilinmiyor | Evet | Güvenilir ikincil kaynak |

Fiyatı bulunmayan ürünlerde döviz fiyatı TL'ye çevrilmemiştir. Ürün bedeli ile montaj bedeli birleştirilmemiş; kurulumun açıkça dâhil olduğu yalnız Vestel ve Arçelik kayıtlarında `Evet`, Tesla'da açıkça hariç olduğu için `Hayır`, diğerlerinde `Bilinmiyor` kullanılmıştır.

## 8. İkinci kaynak doğrulaması

| charger_id | Farklı kaynak URL sayısı | Durum |
|---|---:|---|
| `TESLA_WALL_CONNECTOR_GEN3_TR_22_T2_7M3` | 5 | Doğrulandı |
| `VESTEL_EVC04_AC22_T2P_TR` | 2 | Doğrulandı |
| `ABB_TERRA_AC_W22_SR_0_TR` | 3 | Doğrulandı |
| `WALLBOX_PULSAR_PLUS_22_T2_5M_EU` | 4 | Doğrulandı |
| `SCHNEIDER_CHARGE_EVH5A22N2S_EU` | 5 | Doğrulandı |
| `ZAPTEC_GO_7_4_UK` | 4 | Doğrulandı |
| `EASEE_CHARGE_UP_22_EU` | 2 | Doğrulandı |
| `GOE_CHARGER_GEMINI_11_TR` | 3 | Doğrulandı |
| `HEIDELBERG_HOME_ECO_11_EU_5M` | 2 | Doğrulandı |
| `ARCELIK_AR_AW32_RFID_7_4_TR` | 3 | Doğrulandı |

## 9. Karar desteğinde kullanılabilirlik

- **Yüksek kullanılabilirlik:** nominal AC güç, faz desteği, faza özel azami güç/akım, nominal gerilim, konnektör ve bağlantı tipi. Bu alanlar ürün eleme ve teknik eşleşme için çoğu kayıtta doğrudan kullanılabilir.
- **Orta kullanılabilirlik:** dinamik yük yönetimi, harici sayaç/modül, koruma ayrıntıları, IP/IK ve akıllı özellikler. Özellikler çoğu üründe bulunmakla birlikte aksesuar, ülke ve varyant bağımlılığı ayrıca kontrol edilmelidir.
- **Düşük kullanılabilirlik:** IEC 62955, tam RCD topolojisi, KDV/kurulum fiyat kapsamı ve bazı garanti/fiyat alanları. Eksiklikler ürün aleyhine 'Hayır' olarak yorumlanmamalıdır.
- Pilot, veri şemasının uygulanabilir olduğunu gösterir; ancak güvenli elektrik kurulum uygunluğu için saha keşfi ve yetkili elektrikçi kontrolünün yerine geçmez.

## 10. Şema için olası ileriki eklemeler

Mevcut 71 alan bu pilotta değiştirilmemiştir. İleride veri toplama büyürse aşağıdaki ek alanlar değerlendirilebilir:

- `calisma_kapsami`: görev metninde 'Çekirdek' işareti istenmesine karşın mevcut 71 alanlı şemada bulunmuyor. Bu pilotta eklenmedi.
- `stok_durumu`: 'Satışta' ürünün geçici olarak stokta olmamasını ayrı göstermek için.
- `ekran_tipi` ve `hucresel_baglanti`: LCD/LED ile 4G/eSIM ayrıntılarını Wi-Fi alanına karıştırmamak için.
- `dahili_enerji_sayaci_tipi` ve `sayac_dogruluk_sinifi`: dahili, MID veya yaklaşık ölçüm ayrımını taşımak için.
- `fiyat_para_birimi`: Türkiye dışı fiyatlar ileride dönüşüm yapılmadan tutulacaksa.

## 11. Önerilen sabit veri testleri

- `charger_id` benzersiz ve boş olmamalı.
- `nominal_azami_guc_kw` pozitif olmalı ve faza özel üst sınırdan küçük olmamalı.
- Faz desteği `Hayır` ise ilgili fazın güç/akım alanları null olmalı.
- Ayarlanabilir akım alt sınırı üst sınırdan büyük olmamalı.
- Fiyat doluysa fiyat tarihi ve fiyat kaynak satırı zorunlu olmalı.
- `Evet/Hayır` içeren her kritik koruma ve standart alanı için alan-kaynak kaydı bulunmalı.
- Boş string kullanılmamalı; kategorik bilinmez ile sayısal null ayrımı korunmalı.

## 12. Varsayımlar ve açık noktalar

- Ürün sayfasının aktif olması `Satışta` olarak yorumlandı; anlık mağaza stoğu ayrı alan olmadığı için temsil edilmedi.
- Ürün ailesi belgeleri yalnız seçilen ticari referansla açıkça uyumlu alanlarda kullanıldı; belirsiz opsiyonlar Bilinmiyor bırakıldı.
- Fiyatlar 2026-09-27 erişim tarihli anlık gözlemdir ve teklif niteliği taşımaz.
- Bu rapor veri bulunabilirliğini ve tutarlılığını değerlendirir; ürün performansı, güvenlik üstünlüğü veya satın alma sıralaması yapmaz.
