# 100 Araçlık Veri Setinin Ev Tipi AC Şarj Karar Desteği Açısından Analizi

## Teknik özet

İncelenen `ELEKTRIKLI_ARAC_VERITABANI_100_ARAC.json` dosyası 100 benzersiz
BEV varyantı, 27 marka ve 42 alandan oluşmaktadır. Ev tipi AC şarj cihazının
teknik uyumluluğunu belirleyen konektör, genel AC güç, faz desteği, tek faz
güç/akım ve üç faz destek bilgileri yüksek doluluğa sahiptir. Üç faz güç ve akım
alanlarındaki 10 boş kayıt, üç faz desteği olmayan aynı 10 araçla tam olarak
örtüştüğü için beklenen koşullu boşluktur.

Veri seti karar desteğine doğrudan alınmadan önce iki kritik nokta çözülmelidir:

- Renault Twingo E-Tech 27.5 kWh ve MG MGS5 EV 64 kWh kayıtlarında genel azami
  AC güç `6,6 kW`, tek faz azami güç ise `7,4 kW`dır. Genel üst sınırın faza özel
  üst sınırdan düşük olması alan tanımlarıyla çelişmektedir.
- Kaynak metadata'sı 100 kaydın tamamında doludur; ancak tüm kayıtlar tek bir
  güvenilir ikincil kaynak ailesine dayanmakta, `İkinci kaynak bekleniyor` ve
  `Orta` güven durumundadır. Üretici Türkiye kaynağıyla doğrulanmış kayıt yoktur.

Enerji ihtiyacı hesabına aday `batarya_kullanilabilir_kwh` alanı %100 doludur;
WLTP tüketim ve menzil alanları ise %76 doludur. `zamanlanmis_sarj_destegi` hiç
bilinmemekte, araç üzeri AC şarj cihazının opsiyon durumu yalnız 33 kayıtta
pozitif olarak saptanmakta ve kalan 67 kayıtta `Bilinmiyor`dur.

Bu çalışma bir karar algoritması tasarlamaz. Sınıflandırmalar yalnız alanların
teknik anlamını ve mevcut verinin ev tipi AC şarj seçimine ne ölçüde girdi
olabileceğini gösterir.

## Karar desteği adaylarında doluluk çekirdek AC alanlarında güçlü

Doluluk karşılaştırması, teknik uyumluluk ve kullanıcı enerji ihtiyacı için öne
çıkan alanları aynı 100 araçlık paydada gösterir. Genel AC güç, konektör, faz,
tek faz güç/akım ve kullanılabilir batarya tam doludur. Üç faz güç/akımındaki
%90 oranı beklenen koşullu kapsama karşılık gelir; asıl veri boşlukları araç
üzeri şarj cihazının opsiyon durumu, WLTP değerleri ve zamanlanmış şarjdadır.
Grafik alanın doğruluğunu değil yalnız veri setindeki bilinen değer oranını
gösterir.

## Kapsam ve ölçüm tanımları

- **Analiz birimi:** Bir elektrikli araç varyantı.
- **Payda:** Her alan için 100 kayıt.
- **Dolu:** Değer `null`, boş/yalnız boşluk veya tam olarak `Bilinmiyor` değil.
- **Doluluk yüzdesi:** `dolu kayıt / 100 × 100`.
- **Null:** JSON `null` değeri.
- **Bilinmiyor:** Kontrollü kategorik sentinel değeri.
- **Boş:** Boş string veya yalnız boşluk içeren string.
- **Provenans var:** Kaydın `kaynak_tipi`, `kaynak_basligi`, `kaynak_url`,
  `erisim_tarihi`, `dogrulama_durumu`, `veri_guven_duzeyi` ve `kaynak_notu`
  alanlarının bulunması. Bu provenans kayıt düzeyindedir; tek tek alanlara ayrı
  kaynak bağlanmamıştır.

Şema açıklamaları `create_vehicle_database_template.py` içindeki `FIELDS` ve
`FIELD_GUIDANCE` tanımlarından; sayımlar ve tutarlılık sonuçları doğrudan 100
kayıtlık JSON dosyasından alınmıştır.

## AC uyumluluk alanları yüksek kapsamlı, iki güç kaydı çelişkili

| Alan | Teknik anlam | Birim | Dolu | Null | Bilinmiyor | Boş | Örnek değerler | Provenans |
|---|---|---:|---:|---:|---:|---:|---|---|
| `ac_azami_guc_kw` | Aracın dahili AC şarj cihazının kabul ettiği genel en yüksek AC güç | kW | 100 | 0 | 0 | 0 | `6.6`, `7.4`, `11` (`22` de var) | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_tek_faz_azami_guc_kw` | Tek faz bağlantıda aracın kabul ettiği üst güç | kW | 100 | 0 | 0 | 0 | `6.6`, `7.4` — yalnız 2 farklı değer | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_uc_faz_azami_guc_kw` | Üç faz bağlantıda toplam üst güç | kW | 90 | 10 | 0 | 0 | `11`, `22` — yalnız 2 farklı değer | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_desteklenen_fazlar` | Aracın tek faz veya tek+üç faz kabul yapısı | — | 100 | 0 | 0 | 0 | `Tek ve üç faz`, `Yalnızca tek faz` | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_tek_faz_destegi` | Tek fazlı kaynaktan AC şarj olabilme | — | 100 | 0 | 0 | 0 | Yalnız `Evet` | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_uc_faz_destegi` | Üç fazlı kaynaktan AC şarj olabilme | — | 100 | 0 | 0 | 0 | `Evet`, `Hayır` | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_tek_faz_azami_akim_a` | Tek fazda araç girişinin en yüksek akımı | A | 100 | 0 | 0 | 0 | `29`, `32` — yalnız 2 farklı değer | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_uc_faz_faz_basina_akim_a` | Üç faz şarjda her faz için üst akım | A/faz | 90 | 10 | 0 | 0 | `16`, `32` — yalnız 2 farklı değer | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_konnektor_tipi` | Aracın fiziksel AC giriş tipi | — | 100 | 0 | 0 | 0 | Yalnız `Type 2` | Kayıt düzeyinde var; alan düzeyinde yok |
| `onboard_charger_opsiyonel_mi` | Yazılan dahili AC şarj cihazının standart mı opsiyon mu olduğu | — | 33 | 0 | 67 | 0 | `Evet`, `Bilinmiyor`; `Hayır` yok | Kayıt düzeyinde var; alan düzeyinde yok |
| `ac_sarj_notu` | Ülke, paket, yazılım ve opsiyon istisnaları | — | 100 | 0 | 0 | 0 | Standart faz tablosu notu; opsiyon/ülke farkı ekli not — yalnız 2 şablon | Kayıt düzeyinde var; alan düzeyinde yok |

Genel bir `ac_azami_akim_a` alanı bulunmamaktadır. “AC maksimum akım” iki farklı
bağlama ayrılmıştır: tek faz için `ac_tek_faz_azami_akim_a`, üç faz için faz
başına `ac_uc_faz_faz_basina_akim_a`. Karar desteği açısından doğru ayrım budur;
iki değer toplanarak tek bir akım gibi yorumlanmamalıdır.

AC alan dağılımları:

- Genel azami AC güç: 82 araç `11 kW`, 8 araç `22 kW`, 6 araç `7,4 kW`, 4 araç
  `6,6 kW`.
- Faz yapısı: 90 araç tek ve üç faz, 10 araç yalnız tek faz.
- Tek faz: 98 araç `7,4 kW / 32 A`, 2 araç `6,6 kW / 29 A` olarak kayıtlıdır.
- Üç faz destekleyen 90 aracın 82'si `11 kW / 16 A/faz`, 8'i
  `22 kW / 32 A/faz`dır.

## Batarya ve WLTP alanları enerji ihtiyacını destekliyor, WLTP kapsamı %76

| Alan | Teknik anlam | Birim | Dolu | Null | Bilinmiyor | Boş | Örnek değerler | Provenans |
|---|---|---:|---:|---:|---:|---:|---|---|
| `batarya_kullanilabilir_kwh` | Kullanıcının normal doluluk aralığında kullanabildiği net batarya enerjisi | kWh | 100 | 0 | 0 | 0 | `24`, `79`, `112` | Kayıt düzeyinde var; alan düzeyinde yok |
| `batarya_brut_kwh` | Bataryanın açıklanan toplam teorik kapasitesi | kWh | 100 | 0 | 0 | 0 | `24.3`, `84`, `117` | Kayıt düzeyinde var; alan düzeyinde yok |
| `wltp_tuketim_kwh_100km` | WLTP birleşik testinde 100 km başına enerji tüketimi | kWh/100 km | 76 | 24 | 0 | 0 | `12.2`, `15.1`, `20.4` | Kayıt düzeyinde var; alan düzeyinde yok |
| `wltp_menzil_km` | Tam dolu bataryayla WLTP birleşik menzili | km | 76 | 24 | 0 | 0 | `226`, `623`, `912` | Kayıt düzeyinde var; alan düzeyinde yok |
| `test_standardi` | Menzil ve tüketimin ölçüm standardı | — | 76 | 0 | 24 | 0 | `WLTP`, `Bilinmiyor` | Kayıt düzeyinde var; alan düzeyinde yok |
| `batarya_tuketim_notu` | Jant, donanım, aralık veya veri eksikliği açıklaması | — | 100 | 0 | 0 | 0 | WLTP TEL/TEH uyarısı; WLTP bulunamadı notu — yalnız 2 şablon | Kayıt düzeyinde var; alan düzeyinde yok |

Kullanılabilir kapasite hiçbir kayıtta brüt kapasiteyi aşmamaktadır. WLTP
tüketimi, menzili ve standardı aynı 76 kayıtta birlikte bulunmakta; diğer 24
kayıtta tüketim ve menzil `null`, standart `Bilinmiyor`dur. Bu üç alan arasında
çapraz çelişki tespit edilmemiştir.

## Zamanlanmış şarj verisi kullanılamıyor; DC ve çift yönlü alanlar temel AC seçimi dışında

| Alan | Açıklama | Birim | Dolu | Null | Bilinmiyor | Boş | Örnek değerler | AC seçimindeki konumu |
|---|---|---:|---:|---:|---:|---:|---|---|
| `zamanlanmis_sarj_destegi` | Araç veya üretici uygulaması üzerinden saat planlama desteği | — | 0 | 0 | 100 | 0 | Yalnız `Bilinmiyor` | Akıllı zamanlama gereksinimi için yardımcı olabilirdi; mevcut veri kullanılamaz |
| `dc_konnektor_tipi` | Hızlı DC bağlantı tipi | — | 100 | 0 | 0 | 0 | Yalnız `CCS Combo 2` | Temel ev tipi AC cihaz seçimi için muhtemelen gereksiz |
| `dc_azami_guc_kw` | Aracın tepe DC hızlı şarj gücü | kW | 100 | 0 | 0 | 0 | `40`, `180`, `400` | Ev tipi AC güç sınırını belirlemez |
| `dc_10_80_sure_dakika` | Uygun DC istasyonda %10–80 süresi | dakika | 0 | 100 | 0 | 0 | Yalnız `null` | Hem kapsam dışı hem kullanılamaz |
| `v2l_destegi` | Araçtan cihaza enerji verme | — | 94 | 0 | 6 | 0 | `Evet`, `Hayır`, `Bilinmiyor` | Temel wallbox güç seçimi için muhtemelen gereksiz |
| `v2h_destegi` | Araçtan eve çift yönlü enerji verme | — | 85 | 0 | 15 | 0 | `Evet`, `Hayır`, `Bilinmiyor` | Çift yönlü gelecek senaryosu; temel AC seçimi dışında |
| `v2g_destegi` | Araçtan şebekeye enerji verme | — | 85 | 0 | 15 | 0 | `Evet`, `Hayır`, `Bilinmiyor` | Çift yönlü gelecek senaryosu; temel AC seçimi dışında |
| `sarj_portu_konumu` | Araç üzerindeki şarj kapağının yeri | — | 95 | 0 | 5 | 0 | `Ön orta`, `Sağ arka`, `Sağ ön` | Cihaz yeri ve kablo uzunluğu için teknik yardımcı girdi |

DC alanları AC wallbox gücüyle karıştırılmamalıdır. Örneğin `dc_azami_guc_kw`
değeri 180 kW olan bir aracın ev tipi AC kabulü yine 11 kW olabilir.

## Bütün 42 alanın doluluk ve provenans envanteri

Örnek sütununda veri setinde üçten az farklı değer varsa yalnız mevcut farklı
değerler gösterilmiştir. `Bilinmiyor` ve `null` örneğe eklenebilir, ancak dolu
sayımına dahil edilmemiştir.

| Grup | JSON key | Açıklama | Birim | Dolu | Null | Bilinmiyor | Boş | 3 farklı örnek | Provenans durumu |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| Araç kimliği | `vehicle_id` | Araç varyantına ait benzersiz ve değişmez kimlik | — | 100 | 0 | 0 | 0 | `EU_EVDB_3305_T10F_LONG_RANGE_RWD`; `EU_EVDB_1830_KONA_ELECTRIC_65_KWH_MY24_25`; `EU_EVDB_1945_600E` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `marka` | Üretici/marka adı | — | 100 | 0 | 0 | 0 | `Audi`; `BMW`; `BYD` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `model` | Ticari model adı olarak tasarlanan alan | — | 100 | 0 | 0 | 0 | `T10F Long Range RWD`; `Kona Electric 65 kWh (MY24-25)`; `600e` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `versiyon` | Batarya, çekiş ve şarj donanımını ayıran tam sürüm | — | 100 | 0 | 0 | 0 | `T10F Long Range RWD`; `Kona Electric 65 kWh (MY24-25)`; `600e` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `model_yili_baslangic` | Teknik özelliklerin geçerli olmaya başladığı model yılı | yıl | 100 | 0 | 0 | 0 | `2020`; `2023`; `2024` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `model_yili_bitis` | Teknik özelliklerin geçerliliğinin bittiği model yılı | yıl | 0 | 100 | 0 | 0 | `null` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `pazar` | Teknik özelliklerin geçerli olduğu satış pazarı | — | 100 | 0 | 0 | 0 | Yalnız `Avrupa` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `arac_tipi` | BEV/PHEV ayrımı | — | 100 | 0 | 0 | 0 | Yalnız `BEV` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `uretim_durumu` | Güncel üretim/satış durumu | — | 100 | 0 | 0 | 0 | Yalnız `Satışta` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Araç kimliği | `varyant_notu` | Pazar, paket, jant ve varyant açıklaması | — | 100 | 0 | 0 | 0 | Audi A6 Avant; Audi A6 Sportback; Audi Q6 Sportback için Avrupa varyant notları | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_konnektor_tipi` | Fiziksel AC giriş tipi | — | 100 | 0 | 0 | 0 | Yalnız `Type 2` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_azami_guc_kw` | Genel en yüksek AC kabul gücü | kW | 100 | 0 | 0 | 0 | `6.6`; `7.4`; `11` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_desteklenen_fazlar` | Desteklenen faz yapısı | — | 100 | 0 | 0 | 0 | `Tek ve üç faz`; `Yalnızca tek faz` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_tek_faz_destegi` | Tek faz desteği | — | 100 | 0 | 0 | 0 | Yalnız `Evet` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_tek_faz_azami_guc_kw` | Tek faz üst gücü | kW | 100 | 0 | 0 | 0 | `6.6`; `7.4` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_tek_faz_azami_akim_a` | Tek faz üst akımı | A | 100 | 0 | 0 | 0 | `29`; `32` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_uc_faz_destegi` | Üç faz desteği | — | 100 | 0 | 0 | 0 | `Evet`; `Hayır` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_uc_faz_azami_guc_kw` | Üç faz toplam üst gücü | kW | 90 | 10 | 0 | 0 | `11`; `22`; `null` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_uc_faz_faz_basina_akim_a` | Üç fazda faz başına üst akım | A/faz | 90 | 10 | 0 | 0 | `16`; `32`; `null` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `onboard_charger_opsiyonel_mi` | Dahili AC şarj donanımının opsiyon durumu | — | 33 | 0 | 67 | 0 | `Evet`; `Bilinmiyor` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| AC şarj | `ac_sarj_notu` | Paket/ülke/yazılım/opsiyon istisna notu | — | 100 | 0 | 0 | 0 | Temel faz tablosu notu; opsiyon/ülke farkı ekli not | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Batarya | `batarya_brut_kwh` | Toplam teorik batarya kapasitesi | kWh | 100 | 0 | 0 | 0 | `24.3`; `84`; `117` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Batarya | `batarya_kullanilabilir_kwh` | Normal kullanımda kullanılabilen net kapasite | kWh | 100 | 0 | 0 | 0 | `24`; `79`; `112` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Tüketim | `wltp_tuketim_kwh_100km` | WLTP birleşik tüketim | kWh/100 km | 76 | 24 | 0 | 0 | `12.2`; `15.1`; `20.4` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Tüketim | `wltp_menzil_km` | WLTP birleşik menzil | km | 76 | 24 | 0 | 0 | `226`; `623`; `912` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Tüketim | `test_standardi` | Menzil/tüketim ölçüm standardı | — | 76 | 0 | 24 | 0 | `WLTP`; `Bilinmiyor` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Tüketim | `batarya_tuketim_notu` | Değer aralığı, donanım ve eksik veri notu | — | 100 | 0 | 0 | 0 | TEL/TEH uyarısı; WLTP bulunamadı notu | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `dc_konnektor_tipi` | DC hızlı şarj bağlantı tipi | — | 100 | 0 | 0 | 0 | Yalnız `CCS Combo 2` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `dc_azami_guc_kw` | Tepe DC şarj gücü | kW | 100 | 0 | 0 | 0 | `40`; `180`; `400` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `dc_10_80_sure_dakika` | DC %10–80 şarj süresi | dakika | 0 | 100 | 0 | 0 | `null` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `zamanlanmis_sarj_destegi` | Araç/uygulama üzerinden zamanlama | — | 0 | 0 | 100 | 0 | `Bilinmiyor` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `v2l_destegi` | Araçtan cihaza enerji aktarımı | — | 94 | 0 | 6 | 0 | `Evet`; `Hayır`; `Bilinmiyor` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `v2h_destegi` | Araçtan eve enerji aktarımı | — | 85 | 0 | 15 | 0 | `Evet`; `Hayır`; `Bilinmiyor` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `v2g_destegi` | Araçtan şebekeye enerji aktarımı | — | 85 | 0 | 15 | 0 | `Evet`; `Hayır`; `Bilinmiyor` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Diğer şarj | `sarj_portu_konumu` | Şarj kapağının araç üzerindeki konumu | — | 95 | 0 | 5 | 0 | `Ön orta`; `Sağ arka`; `Sağ ön` | Kayıt düzeyinde 100/100; alan düzeyinde yok |
| Provenans | `kaynak_tipi` | Kaynağın güvenilirlik sınıfı | — | 100 | 0 | 0 | 0 | Yalnız `Güvenilir ikincil kaynak` | Provenansın kendisi; 100/100 |
| Provenans | `kaynak_basligi` | Kullanılan sayfa/belge başlığı | — | 100 | 0 | 0 | 0 | EV Database TOGG T10F; Audi A6 Avant; Hyundai Kona sayfa başlıkları | Provenansın kendisi; 100/100 ve 100 farklı başlık |
| Provenans | `kaynak_url` | Doğrudan kaynak bağlantısı | — | 100 | 0 | 0 | 0 | EV Database araç `3305`; `1830`; `1945` bağlantıları | Provenansın kendisi; 100/100 ve 100 farklı URL |
| Provenans | `erisim_tarihi` | Kaynağın kontrol edildiği tarih | tarih | 100 | 0 | 0 | 0 | Yalnız `2026-07-24` | Provenansın kendisi; 100/100 |
| Provenans | `dogrulama_durumu` | İkinci/resmî kaynak kontrol durumu | — | 100 | 0 | 0 | 0 | Yalnız `İkinci kaynak bekleniyor` | Provenansın kendisi; 100/100 |
| Provenans | `veri_guven_duzeyi` | Kayıt güven sınıfı | — | 100 | 0 | 0 | 0 | Yalnız `Orta` | Provenansın kendisi; 100/100 |
| Provenans | `kaynak_notu` | Çelişki, dönüşüm ve doğrulama notu | — | 100 | 0 | 0 | 0 | EV Database derleme ve Türkiye teknik föyüyle doğrulama uyarısı | Provenansın kendisi; 100/100 ancak tek genel şablon |

## Tutarlılık testlerinde iki yüksek etkili kayıt hatası bulundu

| Kontrol | Sonuç | Etkilenen kayıt | Değerlendirme |
|---|---:|---:|---|
| `vehicle_id` benzersizliği | 100 benzersiz / 100 | 0 | Geçti |
| `kaynak_url` benzersizliği | 100 benzersiz / 100 | 0 | Geçti |
| Genel AC güç = mevcut faz güçlerinin en büyüğü | 98/100 uyumlu | 2 | **Yüksek:** araç tarafı güç sınırı belirsizleşiyor |
| Faz etiketi ↔ tek/üç faz destek alanları | 100/100 uyumlu | 0 | Geçti |
| Destek alanı ↔ faza özel güç/akımın bulunması | 100/100 uyumlu | 0 | Geçti |
| Tek faz güç ≈ `230 V × I` | 100/100, %10 tolerans | 0 | Geçti |
| Üç faz güç ≈ `√3 × 400 V × I/faz` | 90/90, %10 tolerans | 0 | Geçti |
| Kullanılabilir batarya ≤ brüt batarya | 100/100 uyumlu | 0 | Geçti |
| WLTP tüketim ↔ menzil ↔ standart birlikte bulunma | 100/100 uyumlu | 0 | Geçti |
| Boş string kullanımı | 0 boş hücre | 0 | Geçti; eksikler null veya `Bilinmiyor` ile temsil edilmiş |
| Aynı marka+model varyant karşılaştırması | 0 tekrarlı marka+model grubu | — | Sonuç üretilemedi; `model` alanı varyant düzeyinde doldurulmuş |
| Alan düzeyinde kaynak bağlantısı | Yok | 100 | **Yüksek:** aynı satırdaki her değerin tam olarak hangi kaynak bölümünden geldiği makinece izlenemiyor |
| Birincil/Türkiye kaynağıyla doğrulama | 0/100 | 100 | **Yüksek:** üretim kullanımına hazır doğrulama yok |

Çelişkili iki kayıt:

| Araç | Genel azami AC | Tek faz azami | Faz yapısı | Opsiyon alanı | Kaynak notunun işareti |
|---|---:|---:|---|---|---|
| Renault Twingo E-Tech 27.5 kWh | 6.6 kW | 7.4 kW | Yalnızca tek faz | Evet | Kaynak matrisinde daha yüksek opsiyonel/ülkeye bağlı cihaz bulunduğu belirtiliyor |
| MG MGS5 EV 64 kWh | 6.6 kW | 7.4 kW | Yalnızca tek faz | Evet | Aynı opsiyonel/ülkeye bağlı cihaz uyarısı |

Üretim betiğindeki standart AC son işlemi, üç faz gücü genel AC güçten yüksekse
değeri düzeltiyor; tek faz gücü genel AC güçten yüksek olan durumu aynı şekilde
ele almıyor. Bu rapor kod değişikliği yapmamış, yalnız mevcut sonucun etkisini
tespit etmiştir.

## Model ve varyant ayrımı aynı aile içi karşılaştırmayı engelliyor

`marka + model` birleşiminde tekrar eden hiçbir grup yoktur. Bunun nedeni veri
setinde gerçekten aynı model ailesinden yalnız tek araç bulunması olarak
yorumlanamaz: 100 kaydın 93'ünde `model` ve `versiyon` metinleri birebir aynıdır.
Kalan 7 kayıttaki farklar esas olarak marka yazımındaki diakritik farklarıdır
(`Citroen/Citroën`, `Skoda/Škoda`).

Bu nedenle “aynı marka/modelin varyantları arasında beklenmeyen AC farkı var
mı?” kontrolü mevcut alanlarla güvenilir şekilde yapılamamaktadır. Örneğin T10X
Standard Range, Long Range RWD ve Long Range AWD kayıtları insan gözüyle aynı
model ailesine ait görünse de `model` alanında üç ayrı tam varyant adı olarak
tutulmaktadır. Bu rapor, yeni bir model-aile çıkarım kuralı uydurmamıştır.

## Eksik değer kullanımı biçimsel olarak tutarlı, bazı alanlarda anlamsal ayrım zayıf

Toplam 4.200 veri hücresinde 268 `null`, 232 `Bilinmiyor` ve 0 boş string vardır.
Genel desen tutarlıdır: sayısal/tarihsel eksikler `null`, kontrollü kategorik
eksikler `Bilinmiyor` olarak tutulmuştur. Ancak şu anlamsal sınırlamalar vardır:

- `model_yili_bitis` alanındaki 100 `null`, “halen geçerli” ile “bitiş yılı
  bilinmiyor” durumlarını ayırmaz.
- `onboard_charger_opsiyonel_mi` yalnız pozitif `Evet` veya `Bilinmiyor` üretir;
  veri setinde `Hayır` yoktur. Bu nedenle standart donanım ile kaynakta
  opsiyon ifadesinin bulunmaması ayrıştırılamaz.
- `zamanlanmis_sarj_destegi` 100 kaydın tamamında `Bilinmiyor`dur ve karar
  desteğinde kullanılamaz.
- `dc_10_80_sure_dakika` 100 kaydın tamamında `null`dır.
- Üç faz güç/akımındaki 10 `null`, üç faz desteği `Hayır` olan 10 kayıtla
  örtüştüğü için tutarlı koşullu boşluktur.

## Provenans eksiksiz ama kayıt düzeyinde ve henüz ikinci kaynakla doğrulanmamış

Her kayıtta kaynak türü, başlık, URL, erişim tarihi, doğrulama durumu, güven
düzeyi ve kaynak notu bulunmaktadır. 100 URL benzersizdir ve tamamı EV Database
araç sayfalarına aittir. Bununla birlikte:

- Tüm kayıtlar `Güvenilir ikincil kaynak` olarak işaretlidir.
- Tüm kayıtlar `İkinci kaynak bekleniyor` durumundadır.
- Tüm kayıtların güven düzeyi `Orta`dır.
- Pazar alanı 100 kaydın tamamında `Avrupa`dır; Türkiye varyantı olduğu iddia
  edilmemektedir.
- Tek bir kayıt için bile alan bazında ayrı kaynak, kaynak sayfasındaki bölüm,
  ham değer veya dönüşüm kaydı tutulmamıştır.
- WLTP tüketiminin kaynakta Wh/km olarak okunup 10'a bölünmesi gibi dönüşümler
  üretim betiğinde vardır; ancak bu dönüşüm her alan kaydının provenansında
  makinece ayrı işaretlenmez.

Bu nedenlerle veri seti sunum ve şema pilotu için izlenebilir, fakat mevcut
doğrulama durumuyla üretim kararının tek kaynağı olmamalıdır.

## Yöntem ve sağlamlık kontrolleri

Alan profili JSON dosyasının doğrudan okunmasıyla çıkarılmıştır. Her alan için
`null`, boş string ve `Bilinmiyor` ayrı sayılmıştır. Kategorik değerler tam
eşleşmeyle; sayısal değerler JSON sayı tipi üzerinden değerlendirilmiştir.

Tutarlılık kuralları:

1. Genel azami AC güç, mevcut tek/üç faz güçlerinin en büyüğüyle ±0,1 kW içinde
   eşleşmelidir.
2. `Tek ve üç faz` etiketi iki destek alanında da `Evet`; `Yalnızca tek faz`
   etiketi tek fazda `Evet`, üç fazda `Hayır` gerektirir.
3. Destek `Evet` ise ilgili güç ve akım sayısal olmalı; destek `Hayır` ise ilgili
   güç ve akım `null` olmalıdır.
4. Tek faz fizik kontrolünde `P = 230 × I / 1000`, üç fazda
   `P = √3 × 400 × I / 1000` kullanılmış ve yuvarlama için %10 tolerans
   tanınmıştır. Bu kontrol nominal Avrupa gerilimiyle yalnız bariz kombinasyon
   hatalarını arar; araç sertifikasyonu değildir.
5. Kullanılabilir batarya brüt kapasiteyi aşmamalıdır.
6. WLTP tüketim, menzil ve test standardı birlikte dolu veya birlikte eksik
   olmalıdır.

Zamana bağlı geçmiş sürümler bulunmadığı için zaman içindeki şema/doluluk
değişimi incelenememiştir. Kaynak URL'lerin canlı erişilebilirliği ve üretici
sayfalarıyla doğruluğu bu yerel veri denetiminin kapsamında test edilmemiştir.
Alan bazında kesin sayım ve açıklama istendiği için ana kanıt biçimi tablodur;
tek özet grafik yalnız karar desteğiyle yakından ilişkili alanların doluluk
oranlarını karşılaştırır. Bütün 42 alanı aynı grafiğe sıkıştırmak alan adlarını
ve eksik türlerini okunaksızlaştıracağından tam envanter tablolarda korunmuştur.

## Veri setini karar girdisi yapmadan önce gerekli veri düzeltmeleri

Bu maddeler karar algoritması değil, doğrudan tespit edilen veri kalitesi
sorunlarına yönelik en küçük düzeltmelerdir:

1. İki çelişkili araçta genel ve tek faz AC güç alanlarının hangi donanıma ait
   olduğu kaynak üzerinden netleştirilmelidir.
2. `model` alanı model ailesini, `versiyon` alanı tam varyantı temsil edecek
   şekilde kaynak veriden yeniden ayrıştırılmalıdır; böylece aynı model ailesi
   içindeki AC farkları denetlenebilir.
3. Türkiye'de sunulacak varyantlar üretici Türkiye teknik föyü veya kullanım
   kılavuzuyla ikinci kez doğrulanmalı ve doğrulama alanları güncellenmelidir.
4. `onboard_charger_opsiyonel_mi` için `Hayır` ile “kaynakta bilgi bulunamadı”
   ayrımı doğrulanmalıdır.
5. Kullanılması düşünülüyorsa zamanlanmış şarj alanının 100 kayıtta da gerçek
   kaynakla doldurulması gerekir; aksi halde karar girdisi olarak seçilmemelidir.
6. Alan düzeyinde kaynak/ham değer/dönüşüm kaydı bulunması, özellikle AC güç,
   akım ve WLTP alanlarında denetlenebilirliği artıracaktır.

## Açık sorular

- İkinci doğrulamada esas alınacak pazar Türkiye mi, Avrupa mı olacaktır?
- Opsiyonel dahili şarj cihazına sahip araçlarda veri tabanı standart donanımı
  mı, opsiyonlu donanımı mı ayrı varyant olarak tutacaktır?
- `model_yili_bitis:null` “halen geçerli” anlamına mı gelecek, yoksa bilinmeyen
  bitiş yılı için ayrı durum gerekli midir?
- Zamanlanmış şarj özelliği karar desteğinde kullanılacak mı; kullanılmayacaksa
  bu alanın toplanması gerekli midir?

## Son özet: alanların ev tipi AC karar desteğindeki aday rolü

Rol sütununda yalnız istenen dört sınıf kullanılmıştır. Sınıflandırma alanın
teknik anlamına dayanır; karar kuralı önermez.

| Alan | Birim | Doluluk % | Karar desteği için aday rol | Veri kalitesi problemi |
|---|---:|---:|---|---|
| `vehicle_id` | — | 100% | Yardımcı bilgi | Sorun tespit edilmedi; 100 benzersiz |
| `marka` | — | 100% | Yardımcı bilgi | Resmî yazım/diakritik normalizasyonu sınırlı |
| `model` | — | 100% | Yardımcı bilgi | 93 kayıtta `versiyon` ile aynı; model ailesi ayrımı yok |
| `versiyon` | — | 100% | Yardımcı bilgi | `model` alanıyla büyük ölçüde yineleniyor |
| `model_yili_baslangic` | yıl | 100% | Yardımcı bilgi | Sorun tespit edilmedi |
| `model_yili_bitis` | yıl | 0% | Yardımcı bilgi | 100 `null`; devam ediyor/bilinmiyor ayrımı yok |
| `pazar` | — | 100% | Yardımcı bilgi | Yalnız Avrupa; Türkiye varyant kapsamı yok |
| `arac_tipi` | — | 100% | Yardımcı bilgi | Yalnız BEV; PHEV kapsamı yok |
| `uretim_durumu` | — | 100% | Yardımcı bilgi | Yalnız `Satışta`; durum çeşitliliği yok |
| `varyant_notu` | — | 100% | Yardımcı bilgi | Çoğunlukla ortak Avrupa/Türkiye uyarı şablonu |
| `ac_konnektor_tipi` | — | 100% | Teknik uyumluluk girdisi | Yalnız Type 2; diğer konektörler test edilmiyor |
| `ac_azami_guc_kw` | kW | 100% | Teknik uyumluluk girdisi | 2 kayıtta tek faz gücünden düşük |
| `ac_desteklenen_fazlar` | — | 100% | Teknik uyumluluk girdisi | Boolean alanlarla 100/100 uyumlu |
| `ac_tek_faz_destegi` | — | 100% | Teknik uyumluluk girdisi | Tüm kayıtlar `Evet`; negatif/unknown örnek yok |
| `ac_tek_faz_azami_guc_kw` | kW | 100% | Teknik uyumluluk girdisi | 2 kayıtta genel azami güçten yüksek |
| `ac_tek_faz_azami_akim_a` | A | 100% | Teknik uyumluluk girdisi | Güçle fiziksel uyumsuzluk tespit edilmedi |
| `ac_uc_faz_destegi` | — | 100% | Teknik uyumluluk girdisi | Faz etiketiyle 100/100 uyumlu |
| `ac_uc_faz_azami_guc_kw` | kW | 90% | Teknik uyumluluk girdisi | 10 koşullu null, üç fazı desteklemeyen kayıtlarla uyumlu |
| `ac_uc_faz_faz_basina_akim_a` | A/faz | 90% | Teknik uyumluluk girdisi | 10 koşullu null; güçle uyumsuzluk yok |
| `onboard_charger_opsiyonel_mi` | — | 33% | Teknik uyumluluk girdisi | 67 `Bilinmiyor`, hiç `Hayır` yok |
| `ac_sarj_notu` | — | 100% | Yardımcı bilgi | Yalnız 2 genel şablon; alan düzeyi kanıt yok |
| `batarya_brut_kwh` | kWh | 100% | Yardımcı bilgi | Net kapasiteyle çelişki tespit edilmedi |
| `batarya_kullanilabilir_kwh` | kWh | 100% | Kullanıcı ihtiyacı hesabı girdisi | Brüt kapasiteyi aşan kayıt yok |
| `wltp_tuketim_kwh_100km` | kWh/100 km | 76% | Kullanıcı ihtiyacı hesabı girdisi | 24 null; TEL alt sınır seçimi varyanta bağlı belirsizlik taşır |
| `wltp_menzil_km` | km | 76% | Yardımcı bilgi | 24 null |
| `test_standardi` | — | 76% | Yardımcı bilgi | 24 `Bilinmiyor`; WLTP eksikleriyle tutarlı |
| `batarya_tuketim_notu` | — | 100% | Yardımcı bilgi | Yalnız 2 genel not şablonu |
| `dc_konnektor_tipi` | — | 100% | Ev tipi AC şarj seçimi için muhtemelen gereksiz | Yalnız CCS Combo 2; AC ile karıştırılmamalı |
| `dc_azami_guc_kw` | kW | 100% | Ev tipi AC şarj seçimi için muhtemelen gereksiz | AC güç sınırını belirlemez |
| `dc_10_80_sure_dakika` | dakika | 0% | Ev tipi AC şarj seçimi için muhtemelen gereksiz | 100 null |
| `zamanlanmis_sarj_destegi` | — | 0% | Yardımcı bilgi | 100 `Bilinmiyor`; kullanılamaz |
| `v2l_destegi` | — | 94% | Ev tipi AC şarj seçimi için muhtemelen gereksiz | 6 `Bilinmiyor` |
| `v2h_destegi` | — | 85% | Ev tipi AC şarj seçimi için muhtemelen gereksiz | 15 `Bilinmiyor`; çift yönlü sistem ayrı kapsam |
| `v2g_destegi` | — | 85% | Ev tipi AC şarj seçimi için muhtemelen gereksiz | 15 `Bilinmiyor`; çift yönlü sistem ayrı kapsam |
| `sarj_portu_konumu` | — | 95% | Teknik uyumluluk girdisi | 5 `Bilinmiyor`; kablo/yerleşim için kullanılabilir |
| `kaynak_tipi` | — | 100% | Yardımcı bilgi | Tamamı ikincil kaynak |
| `kaynak_basligi` | — | 100% | Yardımcı bilgi | Kayıt düzeyi; alan bazında kaynak ayrımı yok |
| `kaynak_url` | — | 100% | Yardımcı bilgi | 100 benzersiz URL; canlı erişim bu denetimde test edilmedi |
| `erisim_tarihi` | tarih | 100% | Yardımcı bilgi | Tüm kayıtlar aynı tarihte alınmış |
| `dogrulama_durumu` | — | 100% | Yardımcı bilgi | 100/100 ikinci kaynak bekliyor; doğrulanmış kayıt yok |
| `veri_guven_duzeyi` | — | 100% | Yardımcı bilgi | 100/100 Orta; Yüksek güvenli kayıt yok |
| `kaynak_notu` | — | 100% | Yardımcı bilgi | Tek genel not; alan düzeyi dönüşüm/kanıt ayrıntısı yok |
