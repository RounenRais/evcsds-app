# Ev Tipi AC Mode 3 Wallbox Veri Sözlüğü

Bu belge, Türkiye/Avrupa pazarına uygun konut tipi iletken AC Mode 3
wallbox cihazları için ileride yapılacak veri toplamaya ait boş şemayı
tanımlar. Gerçek ürün verisi, karar puanı, kriter ağırlığı veya öneri
algoritması içermez.

## Veri giriş ilkeleri

1. Her kayıt tek bir marka + model + versiyon + pazar + teknik donanım
   birleşimini temsil eder. Güç, kablo, bağlantı veya yük yönetimi farkı
   ayrı `charger_id` gerektirir.
2. Sayısal, tarih, URL ve serbest metin alanında bilgi yoksa Excel hücresi
   boş bırakılır; JSON karşılığı `null` olur. Eksik sayısal bilgi için `0`
   kullanılmaz.
3. Kapalı kategorik alanlarda kaynak bilgi vermiyorsa `Bilinmiyor`
   kullanılır. Araştırılmamış alan boş/null bırakılır; böylece araştırılmamış
   veri ile araştırılıp bulunamamış veri ayrılır.
4. `Evet` ve `Hayır` yalnız açık kaynak kanıtıyla yazılır. Bir özelliğin ürün
   sayfasında yer almaması tek başına `Hayır` kanıtı değildir.
5. Üretici yalnız “dahili koruma var” diyorsa bundan RCD tipi, 6 mA DC
   algılama, RDC-DD veya IEC 62955 uygunluğu çıkarılmaz. İlgili alanlar açık
   teknik beyan yoksa `Bilinmiyor` olur.
6. IEC 61851, IEC 62196, IEC 62955 ve CE alanları yalnız ürün sayfası, teknik
   föy, kurulum kılavuzu veya uygunluk beyanında açıkça bulunuyorsa `Evet`
   yapılır. Ürün türünden standart uyumu varsayılmaz.
7. Koşullu alan uygulanmıyorsa veya üretici sayısal değeri açıklamıyorsa
   `null` bırakılır; gerekçe ilgili not alanında belirtilebilir.

## Zorunluluk değerleri

- **Zorunlu:** Her tamamlanmış kayıtta bir değer bulunmalıdır; kapalı liste
  alanlarında açık bilgi yoksa `Bilinmiyor` kabul edilir.
- **Koşullu:** Bağlı özellik destekleniyorsa veya ana veri mevcutsa doldurulur.
- **İsteğe bağlı:** Kaynakta varsa girilir; yoksa null/boş bırakılır.

## Alanlar

### 1. Kimlik ve kaynak

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `charger_id` | Belirli marka, model, güç, bağlantı, kablo ve pazar varyantını tekil olarak tanımlayan, sonradan değiştirilmemesi gereken benzersiz kayıt kimliği. | Metin | — | Benzersiz sabit kimlik; boşluk kullanılmaması önerilir | Zorunlu | Metadata / provenans |
| `marka` | Ürünü piyasaya sunan üreticinin veya markanın resmî adı. | Metin | — | Üreticinin kullandığı resmî marka adı | Zorunlu | Metadata / provenans |
| `model` | Şarj cihazının üretici tarafından kullanılan ticari model adı. | Metin | — | Üreticinin kullandığı resmî model adı | Zorunlu | Metadata / provenans |
| `versiyon` | Aynı model içindeki güç, kablo, bağlantı, haberleşme veya donanım farkını belirten tam varyant adı. | Metin | — | Üreticinin belirttiği tam varyant; fark yoksa Standart | Zorunlu | Metadata / provenans |
| `pazar` | Teknik özelliklerin ve uygunluk beyanlarının geçerli olduğu satış bölgesi. | Liste | — | Türkiye; Avrupa; Türkiye ve Avrupa; Diğer; Bilinmiyor | Zorunlu | Metadata / provenans |
| `urun_durumu` | Ürünün güncel satış veya üretim durumu. | Liste | — | Satışta; Üretimde; Satışı sona erdi; Duyuruldu; Bilinmiyor | Zorunlu | Metadata / provenans |
| `kaynak_tipi` | Teknik bilginin alındığı belgenin veya sayfanın kaynak sınıfı. | Liste | — | Üretici Türkiye sitesi; Üretici uluslararası sitesi; Üretici teknik föyü; Üretici kullanım/kurulum kılavuzu; Uygunluk beyanı; Sertifikasyon belgesi; Yetkili distribütör; Güvenilir ikincil kaynak | Zorunlu | Metadata / provenans |
| `kaynak_basligi` | Kullanılan web sayfasının, teknik föyün veya belgenin açık başlığı. | Metin | — | Kaynakta görülen belge veya sayfa başlığı | Zorunlu | Metadata / provenans |
| `kaynak_url` | Bilginin doğrulanabileceği doğrudan web veya belge bağlantısı. | URL | — | Geçerli http/https adresi | Zorunlu | Metadata / provenans |
| `erisim_tarihi` | Kaynağın araştırmacı tarafından son kontrol edildiği tarih. | Tarih | — | YYYY-MM-DD | Zorunlu | Metadata / provenans |
| `dogrulama_durumu` | Kaydın ikinci veya daha güçlü bir kaynakla kontrol edilme durumu. | Liste | — | Doğrulanmadı; İkinci kaynak bekleniyor; Doğrulandı; Çelişkili | Zorunlu | Metadata / provenans |
| `veri_guven_duzeyi` | Kaynağın niteliği ve kaynaklar arası uyuma göre kayda verilen genel güven seviyesi. | Liste | — | Yüksek; Orta; Düşük | Zorunlu | Metadata / provenans |
| `kaynak_notu` | Kaynaklar arası fark, ikinci kaynak, sayfa bölümü veya doğrulama sınırlaması gibi provenans ayrıntıları. | Metin | — | Serbest metin; bilinmiyorsa boş/null | İsteğe bağlı | Metadata / provenans |

### 2. AC elektriksel özellikler

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `sarj_modu` | Cihazın IEC 61851 bağlamındaki iletken şarj çalışma modu; bu şablonun kapsamı konut tipi Mode 3 wallbox ürünleridir. | Liste | — | Mode 3; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `nominal_azami_guc_kw` | İncelenen ürün varyantının üretici tarafından açıklanan en yüksek nominal AC çıkış gücü. | Ondalık | kW | Sıfırdan büyük üretici beyanı; bilinmiyorsa null | Zorunlu | Teknik uyumluluk / eleme |
| `tek_faz_destegi` | Cihazın tek fazlı şebekede çalışmayı açıkça destekleyip desteklemediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `tek_faz_azami_guc_kw` | Tek faz bağlantıda cihazın sunabildiği üretici beyanlı en yüksek AC güç. | Ondalık | kW | Pozitif sayı; tek faz desteklenmiyorsa veya değer yoksa null | Koşullu | Teknik uyumluluk / eleme |
| `tek_faz_azami_akim_a` | Tek faz bağlantıda cihazın sağlayabildiği üretici beyanlı en yüksek akım. | Ondalık | A | Pozitif sayı; tek faz desteklenmiyorsa veya değer yoksa null | Koşullu | Teknik uyumluluk / eleme |
| `uc_faz_destegi` | Cihazın üç fazlı şebekede çalışmayı açıkça destekleyip desteklemediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `uc_faz_azami_guc_kw` | Üç faz bağlantıda cihazın sunabildiği üretici beyanlı toplam en yüksek AC güç. | Ondalık | kW | Pozitif sayı; üç faz desteklenmiyorsa veya değer yoksa null | Koşullu | Teknik uyumluluk / eleme |
| `uc_faz_faz_basina_akim_a` | Üç faz çalışmada her bir faz için açıklanan en yüksek akım; toplam akım bu alana yazılmaz. | Ondalık | A/faz | Pozitif sayı; üç faz desteklenmiyorsa veya değer yoksa null | Koşullu | Teknik uyumluluk / eleme |
| `ayarlanabilir_akim_destegi` | Cihazın çıkış akımının kullanıcı, kurulumcu veya yük yönetimi tarafından sınırlandırılabilmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `minimum_ayarlanabilir_akim_a` | Üreticinin izin verdiği ayarlanabilir akım aralığının alt sınırı. | Ondalık | A | Pozitif sayı; ayar desteği yoksa veya değer belirtilmemişse null | Koşullu | Koşullu teknik uygunluk |
| `maksimum_ayarlanabilir_akim_a` | Üreticinin izin verdiği ayarlanabilir akım aralığının üst sınırı. | Ondalık | A | Pozitif sayı ve minimum değerden küçük olmamalı; bilinmiyorsa null | Koşullu | Koşullu teknik uygunluk |
| `nominal_gerilim` | Üreticinin ürün için açıkladığı nominal giriş/çalışma gerilimi veya gerilim aralığı; faz bilgisinden tahmin edilmez. | Metin | V | Üreticinin açık ifadesi; ör. 230 veya 230/400; bilinmiyorsa null | Zorunlu | Teknik uyumluluk / eleme |
| `frekans_hz` | Üreticinin ürün için açıkladığı şebeke frekansı veya desteklenen frekans değeri. | Ondalık | Hz | Pozitif üretici beyanı; bilinmiyorsa null | Zorunlu | Teknik uyumluluk / eleme |

### 3. Araç bağlantısı

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `ac_konnektor_tipi` | Araç tarafında kullanılan AC bağlantı standardı veya cihaz soketi/kablosuyla uyumlu konnektör tipi. | Liste | — | Type 2; Type 1; NACS; GB/T AC; Diğer; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `baglanti_tipi` | Wallbox üzerinde yalnız soket mi bulunduğunu, yoksa araca giden kablonun cihaza sabit mi olduğunu gösterir. | Liste | — | soketli; sabit_kablolu; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `kablo_uzunlugu_m` | Sabit kablolu üründe üretici tarafından belirtilen araç şarj kablosu uzunluğu. | Ondalık | m | Pozitif sayı; soketli üründe veya bilgi yoksa null | Koşullu | Kullanıcı tercihi kriteri adayı |

### 4. Yük yönetimi

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `dinamik_yuk_yonetimi_destegi` | Evdeki anlık tüketimi dikkate alarak şarj gücünü otomatik ayarlayan dinamik yük yönetimi desteği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `dinamik_yuk_yonetimi_dahili_mi` | Dinamik yük yönetimi işlevinin cihazın standart donanımında bulunup bulunmadığı; haricî modül gereksiniminden ayrıdır. | Liste | — | Evet; Hayır; Bilinmiyor | Koşullu | Koşullu teknik uygunluk |
| `harici_enerji_sayaci_gerekli_mi` | Dinamik yük yönetiminin çalışması için ayrı sayaç, akım trafosu veya enerji ölçüm modülü gerekip gerekmediği. | Liste | — | Evet; Hayır; Bilinmiyor | Koşullu | Koşullu teknik uygunluk |
| `uyumlu_yuk_yonetim_modulu` | Üreticinin açıkça uyumlu ilan ettiği haricî sayaç, akım trafosu veya yük yönetim modülü modeli. | Metin | — | Üreticinin belirttiği model/ad; belirtilmemişse null | Koşullu | Koşullu teknik uygunluk |
| `statik_guc_sinirlandirma_destegi` | Kurulum sırasında sabit bir akım veya güç üst sınırı tanımlanabilmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `coklu_sarj_cihazi_yuk_paylasimi` | Birden fazla aynı veya uyumlu şarj cihazının ortak kapasiteyi aralarında paylaştırabilmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Performans kriteri adayı |

### 5. Elektriksel koruma / kurulum

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `dc_kacak_akim_algilama_6ma` | Üründe 6 mA DC kaçak akım algılama işlevinin üretici tarafından açıkça belirtilip belirtilmediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `rdc_dd_destegi` | Üreticinin üründe RDC-DD bulunduğunu veya IEC 62955 kapsamında RDC-DD işlevi sunduğunu açıkça belirtmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `dahili_rcd_tipi` | Cihaz içinde bulunduğu üretici tarafından açıkça belirtilen RCD tipi; genel koruma ifadesinden türetilmez. | Liste | — | Yok; Tip A; Tip B; Tip A-EV; Tip F; Diğer; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `gerekli_harici_rcd_tipi` | Üreticinin kurulum talimatında ayrıca kullanılmasını istediği haricî RCD tipi. | Liste | — | Yok; Tip A; Tip B; Tip A-EV; Tip F; Diğer; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `dahili_asiri_akim_korumasi` | Üründe aşırı akım korumasının dahili olduğu üretici tarafından açıkça belirtiliyorsa Evet olarak kaydedilir. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `koruma_notu` | Koruma cihazlarının kapsamı, standart referansı, haricî eleman şartı ve üretici uyarılarının aynen açıklanacağı alan. | Metin | — | Yalnız üretici beyanına dayalı serbest metin; bilinmiyorsa boş/null | İsteğe bağlı | Koşullu teknik uygunluk |

### 6. Standartlar ve uygunluk beyanları

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `iec_61851_uyumu` | Üreticinin ürün için IEC 61851 uyumunu açıkça beyan edip etmediği; ürün tipinden hareketle varsayılmaz. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `iec_62196_uyumu` | Üreticinin ürün veya konnektör için IEC 62196 uyumunu açıkça beyan edip etmediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `iec_62955_uyumu` | Üreticinin RDC-DD ile ilgili IEC 62955 uyumunu açıkça beyan edip etmediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `ce_beyani` | Ürün için açık CE işareti veya AB Uygunluk Beyanı bulunup bulunmadığı. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Teknik uyumluluk / eleme |
| `standart_notu` | Standart numarası, sürümü, uygunluk belgesi ve beyanın kapsamı gibi ayrıntılar. | Metin | — | Kaynakta açıkça yazılan bilgi; bilinmiyorsa boş/null | İsteğe bağlı | Metadata / provenans |

### 7. Fiziksel ve çevresel özellikler

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `ip_sinifi` | Katı cisim ve su girişine karşı üreticinin beyan ettiği IP koruma sınıfı. | Metin | — | IP ile başlayan üretici beyanı; ör. IP54; bilinmiyorsa null | Zorunlu | Koşullu teknik uygunluk |
| `ik_sinifi` | Mekanik darbeye dayanım için üreticinin beyan ettiği IK sınıfı. | Metin | — | IK ile başlayan üretici beyanı; ör. IK10; bilinmiyorsa null | Zorunlu | Koşullu teknik uygunluk |
| `ic_mekan_uygun` | Üreticinin cihazı iç mekân kurulumu için uygun ilan edip etmediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `dis_mekan_uygun` | Üreticinin cihazı dış mekân kurulumu için uygun ilan edip etmediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Koşullu teknik uygunluk |
| `calisma_sicakligi_min_c` | Üreticinin beyan ettiği çalışma sıcaklığı aralığının alt sınırı. | Ondalık | °C | Üretici beyanlı sayı; bilinmiyorsa null | Koşullu | Koşullu teknik uygunluk |
| `calisma_sicakligi_max_c` | Üreticinin beyan ettiği çalışma sıcaklığı aralığının üst sınırı. | Ondalık | °C | Üretici beyanlı sayı ve minimumdan küçük olmamalı; bilinmiyorsa null | Koşullu | Koşullu teknik uygunluk |

### 8. Akıllı özellikler

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `wifi` | Cihazın Wi-Fi bağlantısını üretici tarafından destekleyip desteklemediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `ethernet` | Cihazın kablolu Ethernet bağlantısını destekleyip desteklemediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `bluetooth` | Cihazın Bluetooth bağlantısını destekleyip desteklemediği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `mobil_uygulama` | Üreticinin cihaz için kullanıcıya yönelik mobil uygulama sunduğunu açıkça belirtmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `zamanlanmis_sarj` | Kullanıcının şarj başlangıç/bitiş zamanını cihaz veya uygulama üzerinden planlayabilmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `rfid` | Kullanıcı yetkilendirmesi için RFID kart veya etiketi desteği. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `ocpp_destegi` | Cihazın Open Charge Point Protocol desteğini üreticinin açıkça belirtmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Performans kriteri adayı |
| `ocpp_surumu` | Üreticinin desteklediğini belirttiği OCPP sürümü; destek yalnızca OCPP olarak yazılmışsa sürüm tahmin edilmez. | Liste | — | 1.6J; 2.0.1; Diğer; Bilinmiyor | Koşullu | Performans kriteri adayı |
| `uzaktan_izleme` | Şarj durumu, hata veya kullanım bilgilerinin uzaktan görüntülenebilmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |
| `enerji_olcumu` | Cihazın aktarılan enerjiyi ölçüp kullanıcıya veya haricî sisteme raporlayabilmesi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Performans kriteri adayı |
| `solar_sarj_destegi` | Fotovoltaik üretime göre şarj gücünü yöneten özel solar/PV şarj işlevi. | Liste | — | Evet; Hayır; Bilinmiyor | Zorunlu | Kullanıcı tercihi kriteri adayı |

### 9. Ekonomi

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `fiyat_tl` | Belirtilen varyantın belirli tarihteki Türkiye satış fiyatı; para birimi dönüşümü yapılmışsa kaynak notunda açıklanır. | Ondalık | TL | Sıfır veya daha büyük sayı; fiyat yoksa null | İsteğe bağlı | Ekonomik kriter adayı |
| `fiyat_tarihi` | Fiyatın geçerli olduğu veya kaynaktan alındığı tarih. | Tarih | — | YYYY-MM-DD; fiyat yoksa null | Koşullu | Ekonomik kriter adayı |
| `fiyata_kdv_dahil_mi` | Kaydedilen fiyatın KDV içerip içermediği. | Liste | — | Evet; Hayır; Bilinmiyor | Koşullu | Ekonomik kriter adayı |
| `kurulum_dahil_mi` | Kaydedilen fiyatın standart kurulumu içerip içermediği. | Liste | — | Evet; Hayır; Bilinmiyor | Koşullu | Ekonomik kriter adayı |
| `garanti_yil` | Üreticinin veya Türkiye distribütörünün ürün için açıkladığı garanti süresi. | Ondalık | yıl | Sıfır veya daha büyük üretici/distribütör beyanı; bilinmiyorsa null | İsteğe bağlı | Ekonomik kriter adayı |

### 10. Açıklama

| Alan | Açıklama | Veri tipi | Birim | İzin verilen değerler | Zorunlu mu? | Karar desteğindeki aday rol |
|---|---|---|---|---|---|---|
| `teknik_not` | Sayısal veya kategorik alanlara sığmayan teknik istisnalar, opsiyonlar ve bağımlılıklar. | Metin | — | Serbest metin; bilinmiyorsa boş/null | İsteğe bağlı | Metadata / provenans |
| `kurulum_notu` | Üreticinin kurulum kılavuzundaki pano, kablo, montaj, haberleşme veya devreye alma koşullarına ilişkin notlar. | Metin | — | Yalnız üretici/kurulum kılavuzu beyanı; bilinmiyorsa boş/null | İsteğe bağlı | Metadata / provenans |
| `varyant_notu` | Güç, bağlantı, kablo, renk, haberleşme modülü veya pazar paketini ayıran varyant açıklaması. | Metin | — | Serbest metin; bilinmiyorsa boş/null | İsteğe bağlı | Metadata / provenans |

## Kapsam dışı

Bu şema DC hızlı şarj istasyonlarını, kamusal şarj işletmeciliğini, karar
puanlarını, kriter ağırlıklarını, ürün sıralamasını ve kurulum uygunluk onayını
kapsamaz. Kablo kesiti, sigorta, RCD/RDC-DD düzeni ve saha uygunluğu nihai
kurulumdan önce yetkili elektrikçi tarafından proje ve üretici talimatlarına
göre doğrulanmalıdır.
