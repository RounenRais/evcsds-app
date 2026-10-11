# 10 Ürünlük Pilot Wallbox Veri Seti – Ürün Seçimi

## Amaç ve kapsam

Bu pilot, mevcut 71 alanlı veri şemasının gerçek üretici belgeleri üzerinde ne ölçüde doldurulabildiğini görmek için hazırlanmıştır. Seçim bir ürün sıralaması veya satın alma önerisi değildir; farklı güç, faz, bağlantı ve yük yönetimi yapılarını temsil eden örneklem oluşturur.

## Seçim ölçütleri

- Türkiye'de satılan veya Avrupa konut pazarında güncel üretici belgesi bulunan AC Mode 3 ürünler.
- Aynı ürün ailesinin belirsiz biçimde birleştirilmesi yerine tekil güç/bağlantı varyantları.
- 7,4 kW, 11 kW ve 22 kW sınıflarının; tek faz, üç faz ve çift faz uyumluluğunun birlikte temsili.
- Soketli ve sabit kablolu cihazların; yerel ayarlı ve akıllı/yük yönetimli cihazların birlikte bulunması.
- Üretici teknik föyü veya kılavuzu olmadan yalnız pazarlama sayfasına dayanan ürünlerin dışarıda bırakılması.

## Seçilen ürün/varyantlar

| # | Marka | Model / varyant | Güç | Faz desteği | Bağlantı | Dinamik yük yönetimi | Pazar |
|---:|---|---|---:|---|---|---|---|
| 1 | Tesla | Wall Connector – 3. Nesil, Type 2, 7,3 m sabit kablo | 22.0 kW | tek faz, üç faz | sabit_kablolu | Evet | Türkiye ve Avrupa |
| 2 | Vestel | EVC04 – AC22-T2P, 22 kW, sabit Type 2 kablo | 22.0 kW | üç faz | sabit_kablolu | Bilinmiyor | Türkiye |
| 3 | ABB | Terra AC – W22-SR-0, 22 kW, Type 2 shutter soket, RFID | 22.0 kW | üç faz | soketli | Evet | Türkiye ve Avrupa |
| 4 | Wallbox | Pulsar Plus – 22 kW, Type 2, 5 m sabit kablo | 22.0 kW | üç faz | sabit_kablolu | Evet | Avrupa |
| 5 | Schneider Electric | Schneider Charge – EVH5A22N2S, 7,4/11/22 kW, T2S soket | 22.0 kW | tek faz, üç faz | soketli | Evet | Avrupa |
| 6 | Zaptec | Zaptec Go – UK, 7,4 kW tek faz, Type 2 soket | 7.4 kW | tek faz | soketli | Evet | Avrupa |
| 7 | Easee | Charge Up – 10141, 1/3 faz, Type 2 soket | 22.0 kW | tek faz, üç faz | soketli | Evet | Avrupa |
| 8 | go-e | Charger Gemini – 11 kW sabit wallbox, Type 2 soket | 11.0 kW | tek faz, üç faz | soketli | Evet | Türkiye ve Avrupa |
| 9 | Heidelberg / Amperfied | Wallbox Home Eco – 11 kW, 5 m Type 2 sabit kablo | 11.0 kW | tek faz, üç faz | sabit_kablolu | Bilinmiyor | Avrupa |
| 10 | Arçelik by WAT | AR AW 32 RFID – 7,4 kW tek faz, 5 m Type 2 sabit kablo | 7.4 kW | tek faz | sabit_kablolu | Bilinmiyor | Türkiye |

## Çeşitlilik özeti

- Güç sınıfları: 7,4 kW = 2 ürün; 11 kW = 2 ürün; 22 kW = 6 ürün.
- Bağlantı: sabit kablolu = 5; soketli = 5.
- Dinamik yük yönetimi: açık destek = 7; açık destek kanıtı bulunamayan = 3. Kaynaklarda açıkça 'desteklenmez' diyen güvenilir bir pilot ürün bulunamadığı için Hayır yazılmadı.
- Pazar dağılımı: Türkiye ve Avrupa = 3; Türkiye = 2; Avrupa = 5.
- Marka sayısı: 10; her marka pilotta tek ürün/varyantla temsil edilmiştir.

## Ürün bazında seçilme gerekçesi

- **Tesla Wall Connector:** Türkiye üretici fiyatı, tek/üç faz kurulumu ve harici sayaçlı dinamik yük yönetimi için güçlü yerel örnek.
- **Vestel EVC04:** Yerli, üç faz 22 kW, sabit kablolu ve montaj dâhil perakende örneği.
- **ABB Terra AC:** Soketli/RFID'li kurumsal ürün, OCPP ve bina enerji yönetimi entegrasyonu örneği.
- **Wallbox Pulsar Plus:** Harici güç ölçerli dinamik yük yönetimi, solar şarj ve ayrıntılı RDC-DD belgelendirmesi örneği.
- **Schneider Charge:** Tek cihazda 7,4/11/22 kW devre uyumu ve harici anti-tripping modülü örneği.
- **Zaptec Go:** Tek faz 7,4 kW UK varyantı ve Zaptec Sense ekosistemi örneği.
- **Easee Charge Up:** Dinamik faz/yük yönetimi, entegre RCD/RDC-DD ve soketli kompakt ürün örneği.
- **go-e Charger Gemini:** 11 kW sabit cihaz, ayrıntılı akım ayarı ve harici Controller ile PV/yük yönetimi örneği.
- **Heidelberg Home Eco:** Ağ özelliği kanıtı sınırlı, yerel ayarlı temel 11 kW wallbox örneği; eksik alan davranışını sınar.
- **Arçelik AW32 RFID:** Türkiye'de satılan tek faz 7,4 kW ürün; resmi sayfadaki kWh/kW birim uyuşmazlığını veri kalite sürecinde görünür kılar.

## Temel kaynaklar

Aşağıdaki bağlantılar seçim gerekçesini ve seçilen tam varyantın temel teknik özelliklerini destekleyen başlıca kaynaklardır. Alan düzeyindeki bütün kaynaklar `WALLBOX_PILOT_ALAN_KAYNAKLARI.xlsx` dosyasında ayrı ayrı kayıtlıdır.

| Ürün/varyant | Temel kaynaklar |
|---|---|
| Tesla Wall Connector – 3. Nesil, 22 kW, 7,3 m | [Tesla Türkiye ürün sayfası](https://shop.tesla.com/tr_tr/product/wall-connector); [Tesla teknik özellikleri](https://energylibrary.tesla.com/docs/Public/Charging/WallConnector/Gen3/Install/3PT2/EMEA/en-us/GUID-0300D171-3BA7-4A8A-BB60-019AB9E31BD5.html) |
| Vestel EVC04-AC22-T2P | [Vestel ürün sayfası](https://www.vestel.com.tr/vestel-evc04-ac22-t2p-elektrikli-arac-sarj-istasyonu--kablolu-p-2321); [Vestel kullanım/kurulum kılavuzu](https://www.vestel-evchargers.com/eu/products/evc-04/files/EVC04_BASE_IB_TR_V1.pdf) |
| ABB Terra AC W22-SR-0 | [ABB Terra AC föyü](https://library.e.abb.com/public/398f504da3a9438e88dd6442979295a0/9AKK107680A2258_en_Leaflet_D_Terra%20AC%20wallbox%20leaflet.pdf); [ABB kullanıcı kılavuzu](https://new.abb.com/docs/librariesprovider53/ep/terra-ac-user-manual-v001.pdf) |
| Wallbox Pulsar Plus 22 kW, 5 m | [Pulsar Plus teknik föyü](https://support.wallbox.com/wp-content/uploads/2022/11/EN_Pulsar_Plus_Datasheet_English.pdf); [Wallbox uygulama sayfası](https://wallbox.com/en/wallbox-app) |
| Schneider Charge EVH5A22N2S | [Schneider resmi ürün sayfası](https://www.se.com/de/de/product/EVH5A22N2S/smarte-wallbox-schneider-charge-22kw-t2-steckdose-6ma-erkennung-innen-au%C3%9Fen-wifi-appsteuerung/); [Schneider teknik veri](https://productinfo.se.com/wiser_home_pacific/viewer?docidentity=TechnicalData-A2742222&extension=xml&lang=en&manualidentity=DeviceUserGuideSchneiderChargeNewEV-63028D82) |
| Zaptec Go UK 7,4 kW | [Zaptec Go teknik föyü](https://help.zaptec.com/objects/sa-migration-assets/aaffa4be-5f88-4e9a-9a9e-c16298de05c7/6ca5df38770187c2cf11854d4a8e9b9fcf17e0ede3959d14592db330005d02cd.pdf); [Zaptec Sense ürün sayfası](https://www.zaptec.com/charging-solutions/zaptec-sense) |
| Easee Charge Up 10141 | [Easee Charge Up teknik föyü](https://download.easee.com/m/2dcca57491b3a0a2/original/-EN-Charge-Up-Productsheet.pdf); [Easee kurulum kılavuzu](https://download.easee.com/m/1a77b7aa5bf8fc3c/original/EN_ChargeUp_InstallationGuide.pdf) |
| go-e Charger Gemini 11 kW | [go-e Türkiye ürün sayfası](https://go-e.com/tr/urunler/go-e-charger-gemini); [go-e Türkçe kurulum ve kullanım kılavuzu](https://go-e.com/fileadmin/Support/Anleitungen/Turkish/kurulum-ve-kullanim-kilavuzu-go-e-sarj-cihazi-gemini-11-22-kw.pdf) |
| Heidelberg / Amperfied Home Eco 11 kW, 5 m | [Home Eco kullanım kılavuzu](https://www.heidelberg-wallbox.eu/media/pdf/09/4e/86/Heidelberg-Wallbox-Eco-Bedienung-ENU.pdf); [Home Eco ürün föyü](https://www.heidelberg-wallbox.eu/media/pdf/45/a5/98/Heidelberg_Wallbox_Home_Eco_Europe_Sell_sheet_1.pdf) |
| Arçelik by WAT AR AW 32 RFID | [Arçelik ürün sayfası](https://www.arcelik.com.tr/elektrikli-arac-sarj-cihazlari/ar-aw-32-rfid-74-kw-elektrikli-arac-sarj-istasyonu); [Arçelik sürdürülebilir enerji kataloğu](https://storage.arcelikkurumsalcozumler.com/arcelikkurumsalcozumler/upload/product/dokumanlar/surdurulebilir_enerji_katalog.pdf) |

## Kapsam sınırı

Pilot yalnız veri toplama ve şema kullanılabilirliği içindir. Ürünlerin teknik veya ekonomik üstünlüğüne ilişkin puan, ağırlık, sıralama ya da satın alma önerisi üretilmemiştir.
