# Karar Destek Sistemi İçin Mevcut Veri Envanteri ve Kod Denetimi

**Denetim tarihi:** 27 Eylül 2026  
**İncelenen dal:** `yolo`  
**Kapsam:** Sayaç tespiti, fatura tespiti, OCR, alan çıkarma, normalizasyon,
geri dönüş davranışı, API çıktıları, testler ve araç/şarj istasyonu veri
varlıkları  
**Kural:** Bu rapor çalışan kodu esas alır. Raporlama sırasında uygulama kodunda
ve modellerde değişiklik yapılmamıştır.

## Yönetici özeti

Mevcut sistem iki görüntü kanalını işleyebilmektedir:

- Sayaç tarafında sayaç bölgesi YOLO ile bulunmakta, PaddleOCR ile yazılar
  okunmakta ve **faz tipi** `monofaz`, `trifaz` veya `belirsiz` olarak
  yapılandırılmaktadır.
- Fatura tarafında fatura bölgesi YOLO ile aranmakta; düşük güven durumunda tam
  görüntü parçalı OCR geri dönüşü çalışmaktadır. OCR metinlerinden sözleşme
  gücü, tüketim, tarife ve bazı yardımcı alanlar yapılandırılmaktadır.

Karar desteğine doğrudan girdi olabilecek en güçlü mevcut standart alanlar
`faz`, `sozlesme_gucu_kw`, `donem_tuketimi_kwh`,
`gunluk_ortalama_kwh`, `tuketici_grubu` ve `tarife` alanlarıdır. Sayaçta OCR
tarafından okunabilen `3x230/400 V` ve `0.25-5(100) A` gibi elektriksel bilgiler
henüz `gerilim_v` veya `azami_akim_a` biçiminde standart değişkenlere
dönüştürülmemektedir.

Fatura alan çıkarıcısı üç alanı kritik saymaktadır:
`sozlesme_gucu_kw`, `donem_tuketimi_kwh` ve `tarife`. Bu alanlardan biri yoksa
veya çıkarılan herhangi bir alanın güveni `0.70` altındaysa çıktı manuel giriş
gerektiğini bildirir. Bununla birlikte, manuel değeri kabul eden veya mevcut
sonuçla birleştiren bir API/form akışı kodda bulunmamaktadır; sistem yalnızca
hangi alanların istenmesi gerektiğini işaretlemektedir.

Projede 100 elektrikli araç varyantı içeren JSON/Excel prototipleri ve bunları
üreten betikler vardır. Ancak bunlar `planning/` altında, Git tarafından henüz
izlenmeyen planlama varlıklarıdır; çalışan API'ye veya bir karar algoritmasına
bağlı değildir. Şarj istasyonu ürün kataloğu, veri tabanı şeması ve eşleştirme
algoritması bulunmamaktadır.

## Denetim yöntemi ve sınırlar

Denetimde kaynak dosyalar satır ve fonksiyon düzeyinde incelenmiş; mevcut bir
sayaç fotoğrafı ve mevcut bir fatura fotoğrafı komut satırından çalıştırılmış;
`test_bill_field_extractor.py` içindeki beş regresyon testi yürütülmüştür. Beş
testin tamamı geçmiştir. Görsel örneklerdeki kişisel veriler bu rapora
aktarılmamıştır.

Bu raporda aşağıdaki ifadeler kesin anlamda kullanılmaktadır:

- **Yapılandırılmış:** Değer program tarafından adlandırılmış bir JSON/dictionary
  alanına dönüştürülmektedir.
- **Yalnızca OCR:** Değer `ocr_metinleri` içinde okunabilir, fakat kendisine ait
  standart alanı yoktur.
- **Manuel giriş işareti:** Sistem alan adını kullanıcıdan istenecek olarak
  listeler; değeri kabul eden bir giriş uç noktası bulunduğu anlamına gelmez.
- **Testli:** İlgili davranış için otomatik assertion içeren test vardır. Tek bir
  görselin elle çalıştırılması otomatik test sayılmamıştır.

## 1. Nihai olarak üretilen tüm yapılandırılmış alanlar

### 1.1. Elektrik altyapısı ve fatura alanları

Arayüzde kullanıcıya gösterilen ayrı etiket tanımları yoktur. Aşağıdaki
“gösterim” adları raporda anlaşılabilirlik için verilmiştir; çalışan API JSON
anahtarlarını döndürmektedir.

| JSON alanı | Gösterim adı | Kaynak | Tip / birim | Gerçek örnek | Üretildiği yer ve yöntem | Güven / düşük güven davranışı | Manuel destek | JSON / otomatik test |
|---|---|---|---|---|---|---|---|---|
| `faz` | Faz tipi | Sayaçtan türetilmiş | Enum-benzeri string; birimsiz | `trifaz` | `predict_and_ocr.py::faz_tespit_et`; normalize OCR üzerinde açık regex örüntüleri, bulunamazsa RapidFuzz | `faz_guvenskor` 0–100. Kural eşleşmesi 100; fuzzy için en az 75 ve adaylar arasında en az 8 puan fark gerekir. Aksi durumda `belirsiz` | Yok | Sayaç üst düzey JSON'unda var; otomatik test yok |
| `sirket.deger` | Elektrik şirketi | Faturadan türetilmiş | Enum-benzeri string | `enerjisa` | `bill_field_extractor.py::fatura_alanlarini_cikar`; tüm normalize OCR metninde şirket ipuçlarına RapidFuzz `partial_ratio` | Ayrı `sirket.guven` 0–1; kabul eşiği `0.78`. Bulunamazsa `bilinmiyor`, `0.0`; manuel listeye eklenmez | Yok | `fatura_bilgileri.sirket` içinde var; Enerjisa test senaryosunda dolaylı kapsanıyor, şirkete özel assertion yok |
| `sozlesme_gucu_kw` | Sözleşme/anlaşma/abonelik gücü | Fatura | Float, kW | `3.0` | `bill_field_extractor.py::_birlesik_guc_alanini_bul` veya `_basit_sayisal_alani_bul`; regex, RapidFuzz, konum, birim ve 0.5–100 kW kontrolü | Alan nesnesinde 0–1 `guven`; `<0.70` ise düşük güven ve manuel liste. Bulunamazsa alan tamamen yoktur | Yalnızca istek işareti | `ozet` ve `alanlar` içinde var; `test_enerjisa_birlesik_guc_satiri`, `test_ayri_yazilmis_sozlesme_gucu` |
| `carpan` | Sayaç çarpanı | Fatura | Float, birimsiz | `1.0` | `_birlesik_guc_alanini_bul`; `Çarpan/Demand/Anl. Gücü` başlığı ile üçlü değerin sıralı eşleştirilmesi | Alan güveni 0–1; `<0.70` genel düşük güven listesine girer. Birleşik yapı yoksa alan yoktur | Yalnızca istek işareti; kritik alan değildir | `ozet` ve `alanlar`; birleşik güç testi |
| `demand_kw` | Demand | Fatura | Float veya `null`, kW | `null` | `_birlesik_guc_alanini_bul`; üçlü değerin ikinci parçası | Alan güveni 0–1. Faturada `-` varsa alan mevcut kalır ve `deger:null` olur; bu “bulunamadı” değil, basılı değer yok anlamındadır | Yalnızca istek işareti; kritik değildir | `ozet` ve `alanlar`; birleşik güç testi `null` değerini doğrular |
| `odenecek_tutar_tl` | Ödenecek tutar | Fatura | Float, TL | `675.0` | `_basit_sayisal_alani_bul`; `Ödenecek` etiketi, konum, sayı ve birim/yasak bağlamları | Alan güveni 0–1; `<0.70` manuel listeye girer. Yoksa alan atlanır | Yalnızca istek işareti; kritik değildir | `ozet` ve `alanlar`; özel assertion yok |
| `gunluk_ortalama_kwh` | Günlük ortalama tüketim | Fatura | Float, kWh/gün | `8.206` | `_gunluk_ortalamayi_bul`; basılı `Fatura Ort.` değeri, satır/konum ve tarih eleme kuralları | Alan güveni 0–1; `<0.70` manuel listeye girer. Kod tüketim/gün hesabı yapmaz | Yalnızca istek işareti; kritik değildir | `ozet` ve `alanlar`; `test_fatura_ortalamasini_yillik_ortalamaya_tercih_eder` |
| `donem_tuketimi_kwh` | Dönem tüketimi | Fatura | Float, kWh | `246.186` | `_donem_tuketimini_bul`; doğrudan etiket veya `Tek Zaman (Endeks)` fark sütunu, konum ve tarih eleme | Alan güveni 0–1; `<0.70` veya eksikse manuel liste | Yalnızca istek işareti | `ozet` ve `alanlar`; birleşik örnek, `test_endeks_farkini_okuma_gunuyle_karistirmaz` ve günlük ortalama testi |
| `tuketici_grubu` | Tüketici/abone grubu | Fatura | String | `Tek Terimli Tek Zamanli ... Mesken AG ...` | `_tuketici_grubunu_bul`; satır içi etiket ve yakın devam satırları | Alan güveni 0–1; `<0.70` manuel listeye girer. Yoksa `tarife` de çoğunlukla üretilemez | Yalnızca istek işareti; kendisi kritik değildir | `ozet` ve `alanlar`; tarife testlerinde dolaylı, metne özel assertion yok |
| `tarife` | Normalize tarife sınıfı | Tüketici grubundan türetilmiş | Kontrollü string | `mesken_tek_zamanli_alcak_gerilim` | `_tarifeyi_siniflandir`; `mesken/sanayi/ticarethane`, `tek/cok zamanli`, `alcak gerilim` belirteçlerinin birleştirilmesi | Tüketici grubunun güvenini devralır; eksik veya `<0.70` ise kritik manuel alan | Yalnızca istek işareti | `ozet` ve `alanlar`; Enerjisa ve ayrı güç testlerinde assertion var |
| `fatura_donemi` | Fatura dönemi | Fatura | String, `AA/YYYY` benzeri | `04/2026` | `_satir_ici_metni_bul`; etiket benzerliği ve tarih regex'i | Alan güveni 0–1; `<0.70` manuel listeye girebilir. Yoksa alan atlanır; kritik değildir | Yalnızca istek işareti | `ozet` ve `alanlar`; yanlış “sonraki okuma dönemi” eşleşmesini reddeden test var, pozitif değere özel assertion yok |
| `son_odeme_tarihi` | Son ödeme tarihi | Fatura | String, tarih | Kod destekli; gerçek örnekte çıkarılmadı | `_satir_ici_metni_bul`; etiket ve `GG.AA.YYYY` benzeri regex | Alan güveni 0–1; düşükse genel manuel listeye girebilir. Parçalı etiket/değer yapısında alan oluşmayabilir | Yalnızca istek işareti; kritik değildir | Üretilirse `ozet` ve `alanlar`; otomatik test yok |
| `sayac_seri_no` | Faturadaki sayaç seri numarası | Fatura | String | Kod destekli; gerçek örnekte ham OCR'da görülüp yapılandırılmadı | `_satir_ici_metni_bul`; etiketle aynı satırda `:` sonrası metin | Alan güveni 0–1; yoksa alan atlanır | Yalnızca istek işareti; kritik değildir | Üretilirse `ozet` ve `alanlar`; otomatik test yok |
| `sayac_tipi` | Faturadaki sayaç tipi | Fatura | String | Kod destekli; gerçek örnekte ham OCR'da `LUN10-F`, ancak alan oluşmadı | `_satir_ici_metni_bul`; etiketle aynı satırda `:` sonrası metin | Alan güveni 0–1; yoksa alan atlanır | Yalnızca istek işareti; kritik değildir | Üretilirse `ozet` ve `alanlar`; otomatik test yok |

Her fatura alanının ayrıntılı kaydı aynı biçimdedir:

```json
{
  "deger": 3.0,
  "birim": "kW",
  "guven": 0.91,
  "etiket": "Çarpan/Demand/Anl. Gücü",
  "ham_deger": "1,000/-/3,000",
  "yontem": "carpan_demand_anlasma_gucu",
  "bbox": {"x1": 2224, "y1": 6321, "x2": 4266, "y2": 6427}
}
```

Bu yapı, nihai değerin hangi OCR metninden ve görüntünün hangi bölgesinden
üretildiğini izlenebilir kılar.

### 1.2. Analiz ve süreç alanları

Bu alanlar doğrudan elektrik altyapısı girdisi değildir; çıktı güvenliği,
izlenebilirlik ve API işletimi için üretilmektedir.

| Alan | Çıktı | Tip / anlam | Üretildiği yer |
|---|---|---|---|
| `sayac_bulundu` | Sayaç | Bool; YOLO'nun sayaç adayı bulup bulmadığı | `predict_and_ocr.py::sayac_analiz_et` |
| `fatura_bulundu` | Fatura | Bool; güvenilir YOLO+OCR veya tam görüntü OCR doğrulaması | `bill_predict_and_ocr.py::fatura_analiz_et`, `_tam_gorsel_ocr_ile_dogrula` |
| `yolo_guveni` | Her ikisi | Float 0–1; seçilen nesne kutusu güveni | Sayaç ve fatura analiz fonksiyonları |
| `bbox` | Her ikisi | Nesne kutusu veya `null` | Sayaç/fatura analiz fonksiyonları |
| `ocr_metinleri` | Her ikisi | OCR kayıt listesi: `text`, `score`, `bbox` | `ocr_engine.py::ocr_calistir` |
| `faz_guvenskor` | Sayaç | Int/float 0–100; faz sınıfı güven göstergesi | `predict_and_ocr.py::faz_tespit_et` |
| `faz_tespit_yontemi` | Sayaç | `kural`, `benzerlik`, `eslesme_yok`, `ocr_hatasi` | Aynı dosya |
| `tespit_yontemi` | Fatura | `yolo_ocr_dogrulama`, `tam_gorsel_ocr`, `yolo` veya `dogrulanamadi` | `bill_predict_and_ocr.py` |
| `ocr_dogrulama_skoru` | Fatura | 0–8 arasında bulunan fatura anahtar kelimesi sayısı | `_fatura_ocr_dogrulama_skoru` |
| `inceleme_gerekli` | Fatura | Bool; aday olup OCR ile doğrulanamayan bazı durumları işaretler | `bill_predict_and_ocr.py` |
| `performans_uyarisi` | Fatura | Düşük YOLO güveninden tam görüntü OCR'a geçildiğinde `dusuk_guvenli_geri_donus`; bazı başarısız sonuçlarda `null` | `_tam_gorsel_ocr_ile_dogrula` |
| `eksik_kritik_alanlar` | Fatura bilgileri | Eksik üç kritik alanın listesi | `bill_field_extractor.py::fatura_alanlarini_cikar` |
| `dusuk_guvenli_alanlar` | Fatura bilgileri | Güveni 0.70 altındaki üretilmiş alanların listesi | Aynı fonksiyon |
| `manuel_giris_gerekli` | Fatura bilgileri | Yukarıdaki iki listenin birleşimi boş değilse `true` | Aynı fonksiyon |
| `manuel_giris_alanlari` | Fatura bilgileri | Eksik ve düşük güvenli alanların sıralanmış birleşimi | Aynı fonksiyon |
| `ozet` | Fatura bilgileri | Üretilen alanların yalnızca `deger` karşılıkları | Aynı fonksiyon |
| `alanlar` | Fatura bilgileri | Kanıt ve güven içeren ayrıntılı alan nesneleri | Aynı fonksiyon |
| `yontem` | Fatura bilgileri | Sabit alan çıkarma yöntemi etiketi | Aynı fonksiyon |
| `hata` | Her ikisi | Okuma/OCR hatasında kullanıcıya dönülen metin; her yanıtta zorunlu değildir | Analiz fonksiyonları |
| `analiz_turu` | API | `sayac` veya `fatura` | `main.py::_gorsel_analiz_et` |
| `kullanici` | API | API anahtarı sahibinin adı | Aynı fonksiyon |
| `islem_suresi_ms` | API | Analiz süresi, ms | Aynı fonksiyon |
| `gorsel.*` | API | Dosya boyutu, özgün/işlenen ölçüler, yeniden boyutlandırma ve gerçek format | `image_processing.py::GorselBilgisi` |

Önemli şema ayrımı: YOLO ve fatura alan güvenleri 0–1 aralığındayken
`faz_guvenskor` 0–100 aralığındadır. Ortak bir güven ölçeği yoktur.

## 2. Sayaçtan elde edilen bilgiler

| Bilgi | Durum | Mevcut davranış ve kanıt |
|---|---|---|
| Faz tipi | **Tam uygulanmış** | `faz` alanına `monofaz`, `trifaz` veya `belirsiz` yazılır. Açık örüntüler önce, RapidFuzz geri dönüşü sonra uygulanır. Gerçek `sayac001.jpg` çalıştırmasında `3x230/400 V` kanıtından `trifaz` üretildi. Otomatik regresyon testi yoktur. |
| Gerilim | **Yalnızca OCR metninde mevcut** | Gerçek örnekte `3x230/400 V- 50 Hz` okundu. Ayrı `gerilim_v`, `faz_faz_gerilim_v` veya `faz_notr_gerilim_v` alanı üretilmiyor. Faz sınıflandırma kuralı bu metni kullanabilir, fakat gerilim değeri yapılandırılmıyor. |
| Akım değerleri | **Yalnızca OCR metninde mevcut** | Gerçek örnekte OCR yaklaşık `0.25-5(100)A` metnini okudu. Başlangıç/temel/azami akım bileşenlerine ayrılmıyor. |
| Maksimum/azami akım | **Yalnızca OCR metninde mevcut** | `5(100) A` içindeki `100 A` ayrı `azami_akim_a` alanına dönüşmüyor. Dolayısıyla karar motoru bunu şu anda standart girdi olarak doğrudan kullanamaz. |
| Sayaç tipi | **Yalnızca OCR metninde mevcut** | Sayaç fotoğrafında `TİP: AELKT.880` benzeri ham metin okunuyor; sayaç analiz çıktısında `sayac_tipi` alanı yoktur. Fatura parser'ındaki aynı adlı isteğe bağlı alan farklı bir kaynaktır. |
| Marka/model | **Yalnızca OCR metninde mevcut** | `KÖHLER`, tip/model ve seri benzeri metinler OCR listesinde vardır; ayrı marka/model alanları üretilmez. |
| Seri numarası | **Yalnızca OCR metninde mevcut** | OCR listesinde seri benzeri değerler vardır; sayaç analizinde yapılandırılmış seri alanı yoktur. |
| Frekans | **Yalnızca OCR metninde mevcut** | `50 Hz` gerilim satırında okunabilir; standart alan yoktur. |
| Standart/sınıf/pulse bilgileri | **Yalnızca OCR metninde mevcut** | EN standardı, sınıf ve benzeri yazılar OCR kayıtlarında bulunabilir; parser yoktur. |
| Sayaçtan manuel doğrulama | **Uygulanmamış** | Sayaç için eksik alan listesi, manuel giriş bayrağı veya kullanıcı değerini kabul eden akış yoktur. |

Sayaç analizi bu nedenle “sayaçtaki bütün elektriksel kapasiteyi çıkaran sistem”
değil, mevcut haliyle “sayacı tespit eden, OCR kanıtını döndüren ve faz tipini
standartlaştıran sistem” olarak tanımlanmalıdır.

## 3. Faturadan elde edilen bilgiler

| Bilgi | Yapılandırılmış çıktı | Durum | Karar desteğinde mevcut kullanılabilirlik |
|---|---|---|---|
| Sözleşme/anlaşma/abonelik gücü | `sozlesme_gucu_kw` | Uygulanmış ve kritik | Konutun sözleşmesel güç sınırını temsil eden doğrudan standart girdi |
| Dönem tüketimi | `donem_tuketimi_kwh` | Uygulanmış ve kritik | Tüketim ölçeği için doğrudan standart girdi |
| Günlük ortalama tüketim | `gunluk_ortalama_kwh` | Uygulanmış, kritik değil | Faturada basılıysa standart girdi; kod tarafından hesaplanmaz |
| Tüketici/abone grubu | `tuketici_grubu` | Uygulanmış | Tarife sınıflandırmasının ham, denetlenebilir metin girdisi |
| Normalize tarife | `tarife` | Uygulanmış ve kritik | `mesken`, zaman türü ve gerilim belirteçlerini birleşik bir sınıfta verir |
| Gerilim seviyesi | Ayrı alan yok; `tarife` içinde ör. `alcak_gerilim` | **Kısmen uygulanmış** | Ayrı gerilim seviyesi değişkeni değildir; yalnızca tüketici grubu metninden türetilen tarife adının parçasıdır |
| Tek/çok zaman | Ayrı alan yok; `tarife` içinde `tek_zamanli`/`cok_zamanli` | **Kısmen uygulanmış** | Ayrı boolean/enum yerine birleşik tarife stringinde temsil edilir |
| Fatura dönemi | `fatura_donemi` | Uygulanmış, kritik değil | Zaman bağlamı olarak kullanılabilir; bulunamazsa çıktıdan atlanır |
| Demand | `demand_kw` | Yalnızca birleşik güç yapısında uygulanmış | Değer varsa kW; basılı `-` için `null`. Kritik alan değildir |
| Çarpan | `carpan` | Yalnızca birleşik güç yapısında uygulanmış | Yardımcı sayaç/fatura bilgisi; kritik alan değildir |
| Ödenecek tutar | `odenecek_tutar_tl` | Uygulanmış, kritik değil | Teknik şarj kapasitesi değil; maliyet/tüketim bağlamı olarak saklanabilir |
| Şirket | `sirket.deger` | Uygulanmış | Şablon/kanıt bağlamı sağlar; elektriksel kapasite değildir |
| Son ödeme tarihi | `son_odeme_tarihi` | Genel kural var, gerçek örnekte oluşmadı | Karar desteği için teknik girdi değildir |
| Faturadaki sayaç seri no | `sayac_seri_no` | Genel satır içi kural var, gerçek örnekte oluşmadı | Kimlik/provenans alanıdır; şarj kapasitesi değildir |
| Faturadaki sayaç tipi | `sayac_tipi` | Genel satır içi kural var, gerçek örnekte oluşmadı | Kod üretirse yardımcı bilgi; elektriksel kapasite parser'ı değildir |

Gerçek Enerjisa örneğinde `son_odeme_tarihi`, `sayac_seri_no` ve `sayac_tipi`
çıktıya girmemiştir. OCR bu bilgilerin bazı parçalarını okumuş olsa da mevcut
satır içi parser etiket ve değeri beklenen biçimde birleştirememiştir.

## 4. OCR'da okunan fakat standart çıktıya dönüştürülmeyen bilgiler

| Kaynak | Ham OCR örneği | Mevcut standart alan | Açıklama |
|---|---|---|---|
| Sayaç | `3x230/400 V- 50 Hz` | Yok | Metin faz tespit kuralını tetikleyebilir; 230 V, 400 V ve 50 Hz ayrı alanlara ayrılmaz. |
| Sayaç | `0.25-5(100)A` benzeri | Yok | Anma/temel/azami akım değerleri ayrıştırılmaz; `100 A` standart azami akım değildir. |
| Sayaç | `KÖHLER` | Yok | Marka alanı yoktur. |
| Sayaç | `TİP: AELKT.880` benzeri | Yok | Sayaç tipi/modeli alanı yoktur. |
| Sayaç | Seri numarası benzeri metinler | Yok | Sayaç fotoğrafı kanalında seri numarası parser'ı yoktur. |
| Sayaç | EN standartları, sınıf ve darbe sabiti benzeri yazılar | Yok | Ham OCR listesinde kalır. |
| Fatura | `Syç Mrk/Seri LUNA/31040811` | Gerçek çıktıda yok | Kod yalnızca uygun satır içi etiket/değer biçimini yakalarsa `sayac_seri_no` üretebilir; bu örnekte üretmedi. |
| Fatura | `Sayaç Tipi LUN10-F` | Gerçek çıktıda yok | Genel `sayac_tipi` kuralı bu görsel düzeninde sonuç üretmedi. |
| Fatura | Parçalara ayrılmış `Son Ödeme Tarihi` ve `20.04.2026` | Gerçek çıktıda yok | Etiket ve tarih farklı OCR satırlarına ayrıldığı için standart alan oluşmadı. |
| Fatura | Ad, adres, TCKN, müşteri/tesisat bilgileri | Yok; fakat ham OCR listesinde API'ye döner | Karar desteği için gereksiz kişisel veriler maskelenmeden `ocr_metinleri` içinde taşınabilmektedir. |

Son satır önemli bir kod-rapor çelişkisidir. Yöntem raporu kişisel alanların
maskelenmesini ve tutulmamasını gereklilik olarak ifade eder; çalışan kod ise
`ocr_metinleri` listesini eksiksiz döndürür. Gerçek fatura denemesinde bu listede
kişisel veri içeren metinler gözlenmiştir. Bu raporda söz konusu değerler
gösterilmemiştir. Mevcut davranışta otomatik maskeleme tespit edilmemiştir.

## 5. Mevcut nihai çıktı şeması

### 5.1. Sayaç analiz çıktısı

Başarılı doğrudan Python çağrısının biçimi:

```json
{
  "sayac_bulundu": true,
  "yolo_guveni": 0.93,
  "bbox": {"x1": 524, "y1": 1301, "x2": 1236, "y2": 2009},
  "faz": "trifaz",
  "faz_guvenskor": 100,
  "faz_tespit_yontemi": "kural",
  "ocr_metinleri": [
    {
      "text": "3x230/400 V- 50 Hz",
      "score": 0.87,
      "bbox": {"x1": 0, "y1": 0, "x2": 0, "y2": 0}
    }
  ]
}
```

Yukarıdaki OCR kutusu yalnızca şemayı göstermek için kısaltılmıştır; gerçek
çıktıda her metnin gerçek görüntü koordinatları bulunur. Sayaç bulunamazsa
`sayac_bulundu:false`, `bbox:null`, `faz:"belirsiz"`, güven `0` ve boş OCR
listesi döner. OCR hata verirse sayaç bulunmuş kalabilir, faz `belirsiz` olur ve
`hata` eklenir.

### 5.2. Fatura analiz çıktısı

Gerçek başarılı örneğin kısaltılmış biçimi:

```json
{
  "fatura_bulundu": true,
  "yolo_guveni": 0.27,
  "bbox": null,
  "tespit_yontemi": "tam_gorsel_ocr",
  "ocr_dogrulama_skoru": 7,
  "ocr_metinleri": ["... koordinatlı OCR kayıtları ..."],
  "inceleme_gerekli": false,
  "performans_uyarisi": "dusuk_guvenli_geri_donus",
  "fatura_bilgileri": {
    "sirket": {"deger": "enerjisa", "guven": 1.0},
    "ozet": {
      "sozlesme_gucu_kw": 3.0,
      "carpan": 1.0,
      "demand_kw": null,
      "odenecek_tutar_tl": 675.0,
      "gunluk_ortalama_kwh": 8.206,
      "donem_tuketimi_kwh": 246.186,
      "tuketici_grubu": "Tek Terimli Tek Zamanli ... Mesken AG ...",
      "tarife": "mesken_tek_zamanli_alcak_gerilim",
      "fatura_donemi": "04/2026"
    },
    "alanlar": {
      "sozlesme_gucu_kw": {
        "deger": 3.0,
        "birim": "kW",
        "guven": 0.91,
        "etiket": "Çarpan/Demand/Anl. Gücü",
        "ham_deger": "1,000/-/3,000",
        "yontem": "carpan_demand_anlasma_gucu",
        "bbox": {"x1": 2224, "y1": 6321, "x2": 4266, "y2": 6427}
      }
    },
    "eksik_kritik_alanlar": [],
    "dusuk_guvenli_alanlar": [],
    "manuel_giris_gerekli": false,
    "manuel_giris_alanlari": [],
    "yontem": "koordinatli_ocr_etiket_konum_sablon_dogrulama"
  }
}
```

`alanlar` gerçek çıktıda `ozet` içindeki her alan için ayrıntılı kanıt taşır.
Alan bulunamazsa çoğu alan `null` ile doldurulmaz; hem `ozet` hem `alanlar`
içinden tamamen atlanır. İstisna, birleşik güç dizisinde `-` ile gösterilen
`demand_kw` değeridir; alan mevcut, değer `null` olur.

### 5.3. FastAPI sarmalayıcısı

`/analyze`, `/analyze/meter` ve `/analyze/bill` uç noktaları ilgili analiz
çıktısına aşağıdaki alanları ekler:

```json
{
  "analiz_turu": "fatura",
  "kullanici": "api_anahtari_sahibi",
  "islem_suresi_ms": 12345,
  "gorsel": {
    "dosya_boyutu": 1234567,
    "orijinal_genislik": 6912,
    "orijinal_yukseklik": 9216,
    "islenen_genislik": 4500,
    "islenen_yukseklik": 6000,
    "yeniden_boyutlandirildi": true,
    "kaynak_format": "JPEG"
  }
}
```

API JPEG, PNG ve WebP kabul eder; dosya sınırı 25 MB, çözünürlük sınırı 80
megapiksel, işlenen en uzun kenar 6000 pikseldir. Bu metadata elektriksel karar
girdisi değildir.

## 6. Eksik / belirsiz alan politikası

### Fatura

Kodun mevcut politikası şöyledir:

1. Kritik alanlar `sozlesme_gucu_kw`, `donem_tuketimi_kwh` ve `tarife`dir.
2. Kritik alanlardan biri hiç üretilemezse `eksik_kritik_alanlar` listesine
   eklenir.
3. Üretilmiş herhangi bir alanın güveni `0.70` altındaysa
   `dusuk_guvenli_alanlar` listesine eklenir. Bu kural yalnız kritik alanlarla
   sınırlı değildir.
4. İki listenin birleşimi `manuel_giris_alanlari` olur; liste boş değilse
   `manuel_giris_gerekli:true` döner.
5. Düşük güvenli değer `ozet` ve `alanlar` içinden silinmez veya `null` yapılmaz;
   değer korunur ve ayrıca işaretlenir.
6. Bulunamayan alanlar genel olarak JSON'dan atlanır; sistem değer tahmin etmez.
7. `demand_kw:null`, birleşik alanda gerçek OCR parçası `-` olduğunda bilinçli
   olarak üretilebilir.
8. Manuel alanları kabul eden, doğrulayan veya otomatik sonuçla birleştiren bir
   endpoint/fonksiyon yoktur. Kullanıcıdan tekrar bilgi istenmesi yalnızca JSON
   bayrağı ve alan listesi seviyesindedir.

Alan adayı oluşturulurken etiket benzerliği için `0.72` eşiği kullanılır. Genel
eşleştirme puanı yaklaşık olarak şöyledir:

```text
alan_guveni = 0.42 × etiket_benzerligi
              + 0.38 × uzamsal_yakinlik
              + 0.20 × OCR_guveni
```

Bu uygulamaya özgü sezgisel puandır; kalibre edilmiş olasılık değildir.

Fatura tespitinde YOLO aday eşiği `0.25`, güvenilir kabul eşiği `0.50`dir.
Güven `0.50` altındaysa tam görüntü OCR çalışır. Sekiz fatura anahtarından en az
ikisi bulunursa fatura doğrulanır. Bu doğrulama skoru alan çıkarma güveninden
farklıdır.

### Sayaç

Sayaç YOLO eşiği `0.50`dir. Açık faz örüntüsü bulunursa faz güveni 100 olur.
Fuzzy geri dönüşte en yüksek skor en az 75 ve monofaz/trifaz skor farkı en az 8
olmalıdır. Sağlanmazsa `faz:"belirsiz"` döner. Sayaç için manuel giriş bayrağı
ve eksik alan listesi yoktur.

## 7. Kullanıcıdan şu anda alınan bilgiler

| Girdi | Mevcut mu? | Açıklama |
|---|---|---|
| Sayaç görseli | Evet | Multipart dosya; `/analyze` veya `/analyze/meter` |
| Fatura görseli | Evet | Multipart dosya; `/analyze/bill` |
| `X-API-Key` | Evet | Erişim doğrulaması için HTTP başlığı |
| API anahtarı üretiminde kullanıcı adı | Evet | Yönetici korumalı `/keys/generate`; karar desteği girdisi değildir |
| Manuel sözleşme gücü/tüketim/tarife | Hayır | Yalnızca bu alanların istenmesi gerektiğini belirten çıktı vardır |
| Araç marka/model/varyant seçimi | Hayır | Planlama veri dosyası vardır, fakat çalışan API'de kullanıcı girdisi değildir |
| Günlük kilometre | Hayır | Mevcut değil |
| Bütçe | Hayır | Mevcut değil |
| Park/şarj süresi | Hayır | Mevcut değil |
| İstenen şarj süresi | Hayır | Mevcut değil |
| Evde eşzamanlı yük | Hayır | Mevcut değil |
| Sigorta, kablo, pano, RCD, topraklama bilgileri | Hayır | Mevcut değil |
| Tarife tercihi veya zaman planı | Hayır | Mevcut değil |

## 8. Araç ve şarj istasyonu tarafında mevcut yapı

### 8.1. Elektrikli araçlar

`planning/` klasöründe araç veri tabanı için geliştirilmiş bağımsız prototip
varlıkları bulunmaktadır:

- `create_vehicle_database_template.py`: Excel veri toplama şablonunu üretir.
- `build_100_vehicle_database.py`: örnek araç kayıtlarını derler ve dışa aktarır.
- `ELEKTRIKLI_ARAC_VERITABANI_100_ARAC.json`: 100 araç varyantı.
- `ELEKTRIKLI_ARAC_VERITABANI_100_ARAC.xlsx`: aynı örnek veri kümesinin Excel
  sunumu.
- V1/V2/V3 Excel şablonları.

JSON dosyasında 100 kayıt, 27 marka ve kayıt başına 42 alan vardır. Alan grupları
şöyledir:

- **Kimlik:** `vehicle_id`, `marka`, `model`, `versiyon`, model yılı başlangıç ve
  bitişi, pazar, araç tipi, üretim durumu, varyant notu.
- **AC şarj:** konektör, azami AC güç, desteklenen fazlar, tek/üç faz desteği,
  faza göre güç ve akım, dahili şarj donanımının opsiyon durumu, not.
- **Batarya/tüketim:** brüt ve kullanılabilir batarya, WLTP tüketim ve menzil,
  test standardı, not.
- **Diğer şarj özellikleri:** DC konektörü/gücü, 10–80 süre alanı, zamanlanmış
  şarj, V2L/V2H/V2G, şarj portu konumu.
- **Kaynak/provenans:** kaynak türü, başlık, URL, erişim tarihi, doğrulama ve
  güven düzeyi, kaynak notu.

Bu varlıkların mevcut sınırları:

- Çalışan FastAPI uygulamasına import edilmezler.
- Supabase veya başka bir veri tabanı şeması/migrasyonu yoktur.
- Araç seçme/sorgulama endpoint'i yoktur.
- Sayaç/fatura sonucuyla araç kaydını eşleştiren karar mantığı yoktur.
- `planning/` klasörü denetim anında Git tarafından izlenmemektedir.
- 100 kayıt içindeki bazı alanlar eksiktir: model yılı bitişi ve DC 10–80 süre
  alanlarının tamamı; üç faz güç/akım alanlarının 10'u; WLTP tüketim ve menzil
  alanlarının 24'ü boştur. Bazı diğer eksikler `null` yerine `Bilinmiyor` enumu
  ile temsil edilmektedir.

Dolayısıyla araç veri yapısı mevcuttur, fakat çalışan sistem bileşeni değildir.

### 8.2. Şarj istasyonları

Şarj istasyonu ürünleri için aşağıdaki alanları içeren katalog, JSON/Excel veri
kaynağı, veri tabanı tablosu, API veya sınıf tespit edilmemiştir:

| Alan grubu | Durum |
|---|---|
| Güç | Yok |
| Faz desteği | Yok |
| Akım | Yok |
| Soket/kablo tipi | Yok |
| Dinamik yük yönetimi | Yok |
| Fiyat | Yok |
| Garanti | Yok |
| Akıllı özellikler | Yok |

Raporlarda gelecekteki wallbox/şarj istasyonu önerisinden söz edilmesi çalışan
bir ürün kataloğu veya karar algoritması bulunduğu anlamına gelmemektedir.

## 9. Türetilen / hesaplanan değerler

| Değer | Doğrudan OCR mı? | Mevcut kod mantığı |
|---|---|---|
| `faz` | Hayır | Normalize OCR metni açık monofaz/trifaz regex'leriyle sınıflandırılır; sonra iki RapidFuzz skoru karşılaştırılır. |
| `faz_guvenskor` | Hayır | Açık kuralda 100; fuzzy durumda en yüksek benzerlik skoru; koşul sağlanmazsa 0. |
| `sirket` | Hayır | Tüm OCR metninin tanımlı şirket ipuçlarıyla en yüksek `partial_ratio` skoru; eşik 0.78. |
| `tarife` | Hayır | Tüketici grubu metninde bulunan sınıf, zaman ve gerilim belirteçleri `_` ile birleştirilir. Ayrı tarife tablosu kullanılmaz. |
| Alan `guven` değeri | Hayır | Etiket benzerliği, uzamsal yakınlık ve OCR güveninin 0.42/0.38/0.20 ağırlıklı toplamı; bazı özel kurallarda ek kural puanları kullanılır. |
| `carpan`, `demand_kw`, `sozlesme_gucu_kw` | Kısmen | Tek ham `1,000/-/3,000` dizisi etiket sırasına göre üç ayrı standart alana ayrılır. Sayısal kısımlar Türkçe ondalık biçiminden float'a çevrilir. |
| `donem_tuketimi_kwh` | Değer OCR'dan okunur | Kod önce/son endeks farkını kendisi hesaplamaz; faturada basılı fark sütunundaki değeri konumla seçer. |
| `gunluk_ortalama_kwh` | Değer OCR'dan okunur | Kod dönem tüketimini gün sayısına bölmez; faturada basılı “Fatura Ort.” değerini seçer. |
| `ocr_dogrulama_skoru` | Hayır | Sekiz anahtarın OCR metninde bulunma sayısıdır; en az 2 fatura doğrulaması için yeterlidir. |
| `fatura_bulundu` | Hayır | Güvenilir YOLO ve OCR doğrulaması veya tam görüntü OCR skorunun en az 2 olmasıyla belirlenir. |
| `eksik_kritik_alanlar` | Hayır | Üç kritik anahtarın `alanlar` sözlüğünde bulunmamasına göre üretilir. |
| `dusuk_guvenli_alanlar` | Hayır | Üretilmiş alanlardan güveni 0.70 altındakiler seçilir. |
| `manuel_giris_gerekli` | Hayır | Eksik kritik ve düşük güvenli alan birleşimi boş değilse `true`. |
| OCR global `bbox` | Hayır | Parçalı OCR'da parça ofsetleri yerel koordinatlara eklenir. |
| OCR tekilleştirme | Hayır | Aynı metin ve en az 0.35 IoU taşıyan örtüşen parça sonuçlarından yüksek güvenli olan korunur. |
| Görsel yeniden boyutlandırma bilgisi | Hayır | En uzun kenar 6000'i aşarsa oran korunarak küçültülür ve durum metadata'ya yazılır. |
| `islem_suresi_ms` | Hayır | Analiz başlangıç/bitiş süre farkı milisaniyeye çevrilir. |

## 10. Karar destek sistemi açısından olası veri envanteri

Bu bölüm yeni karar algoritması önermemekte, yalnız mevcut kodun sağladığı
verileri sınıflandırmaktadır.

### A. Şu anda otomatik ve yapılandırılmış biçimde elde edilebilen bilgiler

- Sayaç faz tipi.
- Fatura şirketi.
- Sözleşme/anlaşma gücü.
- Dönem tüketimi.
- Günlük ortalama tüketim; yalnız faturada basılı değer yakalanırsa.
- Tüketici/abone grubu.
- Birleşik normalize tarife sınıfı.
- Fatura dönemi.
- Birleşik güç alanı varsa çarpan ve demand.
- Ödenecek tutar.
- Şablona bağlı olarak son ödeme tarihi, faturadaki sayaç seri numarası ve sayaç
  tipi.
- Her alanın kanıtı, güveni, ham OCR değeri, yöntemi ve koordinatı.
- Tespit doğrulama, eksik alan ve düşük güven metadata'sı.

### B. OCR'da görülen fakat henüz yapılandırılmamış bilgiler

- Sayaç gerilim değerleri.
- Frekans.
- Sayaç akım aralığı ve azami akım.
- Sayaç fotoğrafındaki marka, model/tip ve seri numarası.
- Sayaç standart, sınıf ve darbe/pulse bilgileri.
- Mevcut gerçek faturada parser'ın yakalayamadığı sayaç marka/seri, sayaç tipi
  ve parçalı son ödeme tarihi.
- Kişisel ve abonelik bilgileri; bunlar karar girdisi değildir ve ham OCR içinde
  dönebilmektedir.

### C. Kullanıcı tarafından manuel doğrulanabilen/girilebilen bilgiler

Çalışan kodda manuel değer kabul eden bir mekanizma yoktur. Yalnızca fatura
çıktısı kullanıcıdan şu alanların istenmesi gerektiğini işaretleyebilir:

- `sozlesme_gucu_kw`
- `donem_tuketimi_kwh`
- `tarife`
- Güveni 0.70 altına düşen diğer üretilmiş alanlar

Bu nedenle bu bölümde “giriş desteği var” denemez; mevcut olan yalnızca manuel
giriş ihtiyacının makinece okunabilir biçimde bildirilmesidir.

### D. Projede hiç bulunmayan bilgiler

- Kullanıcının seçtiği araç ve çalışan araç sorgu akışı.
- Günlük sürüş mesafesi, hedef doluluk, mevcut batarya yüzdesi.
- Kullanılabilir gece/park/şarj süresi.
- Kullanıcı bütçesi.
- Evde eşzamanlı yük ve kullanılabilir artık güç.
- Ana sigorta, hat sigortası, kablo kesiti, pano kapasitesi, RCD ve topraklama
  durumunun yapılandırılmış girdileri.
- Şarj istasyonu ürün kataloğu ve ürün fiyat/garanti/özellik alanları.
- Araç + altyapı + şarj istasyonu eşleştirme ve sıralama algoritması.
- Öneri, gerekçe, uygun/uygunsuz sonucu veya kurulum onayı üreten nihai karar
  çıktısı.

## 11. Dosya haritası

| Dosya | Temel görev | Ürettiği/işlediği alanlar |
|---|---|---|
| `predict_and_ocr.py` | Sayaç YOLO tespiti, kırpma, OCR ve faz sınıflandırma | `sayac_bulundu`, YOLO/bbox, `faz`, faz güven/yöntem, OCR listesi |
| `bill_predict_and_ocr.py` | Fatura YOLO tespiti, OCR doğrulama, düşük güvenli tam görüntü geri dönüşü | Fatura zarf alanları ve `fatura_bilgileri` |
| `bill_field_extractor.py` | Koordinatlı OCR'dan standart fatura alanları çıkarma | Şirket, güç, tüketim, tarife, dönem, tutar ve yardımcı alanlar; manuel işaretler |
| `ocr_engine.py` | PaddleOCR, 1800 px örtüşmeli parçalama, koordinat taşıma ve tekrar temizleme | `text`, `score`, `bbox` OCR kayıtları |
| `image_processing.py` | Yükleme doğrulama, EXIF yönü, RGB/JPEG dönüşümü ve boyut sınırı | `GorselBilgisi` metadata'sı |
| `main.py` | FastAPI uç noktaları, API anahtarı kontrolü, geçici dosya ve API sarmalı | Analiz türü, kullanıcı, süre, görsel metadata'sı |
| `api_keys.py` | API anahtarı üretme/saklama/doğrulama | Erişim kimliği; elektriksel veri üretmez |
| `test_bill_field_extractor.py` | Fatura alan çıkarma regresyon testleri | Güç, tüketim, tarife, dönem yanlış eşleşmesi, günlük ortalama |
| `model_test.py` | Eski/elle model görselleştirme betiği | Otomatik test değildir; sabit eski `C:\EASIOS\...` yolları ve GUI kullanır |
| `bill_model_train.py` | Fatura YOLO eğitim betiği | Eğitim konfigürasyonu; çalışma zamanı alanı üretmez |
| `bill_scene_model_train.py` | Fatura sahne modeli eğitim denemesi | Eğitim/deney; karar verisi üretmez |
| `planning/create_vehicle_database_template.py` | Araç Excel şablonu üretimi | 42 alanlı araç veri sözlüğü/şablonu |
| `planning/build_100_vehicle_database.py` | 100 örnek araç veri kümesi üretimi | Araç, AC/DC şarj, batarya, WLTP ve kaynak alanları |
| `planning/ELEKTRIKLI_ARAC_VERITABANI_100_ARAC.json` | Bağımsız örnek araç veri kümesi | 100 varyant; API ile bağlı değil |
| `FATURA_ANALIZ_YONTEMI_RAPORU.md` | Yöntem ve deney raporu | Çalışan kod değildir; bazı hedefleri/gelecek işleri anlatır |

## 12. Test durumu

`python -m unittest -v test_bill_field_extractor.py` komutu çalıştırılmış ve
aşağıdaki beş testin tamamı geçmiştir:

| Test | Doğrulanan davranış |
|---|---|
| `test_enerjisa_birlesik_guc_satiri` | `1,000/-/3,000` değerinden 3.0 kW, çarpan 1.0, demand `null`, 246.186 kWh ve tarife; manuel giriş gerekmez |
| `test_ayri_yazilmis_sozlesme_gucu` | Ayrı `Sözleşme Gücü: 5,00 kW`, 185.2 kWh ve çok zamanlı mesken tarifesi |
| `test_sonraki_okuma_donemini_fatura_donemi_sanmaz` | “Sonraki Okuma Dönemi” yanlışlıkla fatura dönemi yapılmaz; kritik alan eksikleri manuel işaretlenir |
| `test_endeks_farkini_okuma_gunuyle_karistirmaz` | Okuma günü 30 yerine fark sütunundaki 246.186 seçilir |
| `test_fatura_ortalamasini_yillik_ortalamaya_tercih_eder` | Fatura ortalaması yıllık ortalamaya tercih edilir ve tarih tüketim sayılmaz |

Otomatik olarak test edilmediği tespit edilen kritik alanlar/davranışlar:

- Sayaç tespiti, sayaç OCR'sı, monofaz/trifaz/belirsiz sınıflandırması ve fuzzy
  eşikler.
- Sayaç gerilim ve akımının yapılandırılması; zaten uygulanmamıştır.
- Fatura YOLO tespiti, düşük güvenli tam görüntü OCR geri dönüşü ve anahtar kelime
  doğrulaması.
- Şirket sınıflandırmasına özel assertion.
- Ödenecek tutar.
- Tüketici grubunun çok satırlı birleştirilmesi.
- Gerilim ve zaman sınıflarının ayrı davranışları.
- Pozitif fatura dönemi, son ödeme tarihi, sayaç seri no ve sayaç tipi.
- Düşük güvenli **mevcut** bir alanın `<0.70` ile manuel listeye girmesi.
- API kimlik doğrulama, dosya sınırları, görsel dönüşümü ve çıktı sarmalı.
- OCR parçalama, global koordinat ve IoU tekilleştirme.
- Araç veri kümesi doğruluğu, veri tabanı aktarımı, şarj istasyonu verisi ve karar
  algoritması.

`model_test.py` otomatik test altyapısı değildir. Eski mutlak dizinler kullanır,
etkileşimli pencere açar ve çıktı görselleri yazar; güncel iş akışının regresyon
kanıtı sayılmamalıdır.

## 13. Örnek senaryolar

### 13.1. Başarılı sayaç analizi

Mevcut `sayac_photos/sayac001.jpg` ile gerçek çalıştırmadan alınan özet:

```json
{
  "sayac_bulundu": true,
  "yolo_guveni": 0.93,
  "bbox": {"x1": 524, "y1": 1301, "x2": 1236, "y2": 2009},
  "faz": "trifaz",
  "faz_guvenskor": 100,
  "faz_tespit_yontemi": "kural",
  "ocr_kanit_ornekleri": [
    {"text": "KÖHLER", "score": 0.99},
    {"text": "TÍP: AELKT.880", "score": 0.93},
    {"text": "3x230/400 V- 50 Hz", "score": 0.87},
    {"text": "0.25-5(100)A", "score": 0.74}
  ]
}
```

Yalnız `faz` standart elektriksel alandır. Gerilim, frekans, tip ve akım bu
örnekte ham OCR kanıtıdır.

### 13.2. Başarılı fatura analizi

Mevcut `electric_bills_test_image.jpg` ile gerçek çalıştırmadan alınan özet:

```json
{
  "fatura_bulundu": true,
  "yolo_guveni": 0.27,
  "bbox": null,
  "tespit_yontemi": "tam_gorsel_ocr",
  "ocr_dogrulama_skoru": 7,
  "inceleme_gerekli": false,
  "performans_uyarisi": "dusuk_guvenli_geri_donus",
  "fatura_bilgileri": {
    "sirket": {"deger": "enerjisa", "guven": 1.0},
    "ozet": {
      "sozlesme_gucu_kw": 3.0,
      "carpan": 1.0,
      "demand_kw": null,
      "odenecek_tutar_tl": 675.0,
      "gunluk_ortalama_kwh": 8.206,
      "donem_tuketimi_kwh": 246.186,
      "tarife": "mesken_tek_zamanli_alcak_gerilim",
      "fatura_donemi": "04/2026"
    },
    "eksik_kritik_alanlar": [],
    "dusuk_guvenli_alanlar": [],
    "manuel_giris_gerekli": false,
    "manuel_giris_alanlari": []
  }
}
```

Bu örnek aynı zamanda fatura YOLO güveni düşük olsa bile tam görüntü parçalı
OCR'ın alan çıkarma sürecini tamamlayabildiğini göstermektedir. “Düşük güvenli
geri dönüş” alan değerlerinin düşük güvenli olduğu anlamına gelmez; YOLO yerine
daha pahalı OCR yolunun kullanıldığını ifade eder.

### 13.3. Manuel giriş işareti üreten analiz

`test_sonraki_okuma_donemini_fatura_donemi_sanmaz` senaryosundaki gerçek alan
çıkarıcı sonucu:

```json
{
  "sirket": {"deger": "bilinmiyor", "guven": 0.0},
  "ozet": {},
  "alanlar": {},
  "eksik_kritik_alanlar": [
    "sozlesme_gucu_kw",
    "donem_tuketimi_kwh",
    "tarife"
  ],
  "dusuk_guvenli_alanlar": [],
  "manuel_giris_gerekli": true,
  "manuel_giris_alanlari": [
    "donem_tuketimi_kwh",
    "sozlesme_gucu_kw",
    "tarife"
  ],
  "yontem": "koordinatli_ocr_etiket_konum_sablon_dogrulama"
}
```

Burada değer uydurulmamış ve kritik alanlar `null` ile doldurulmamıştır;
alanlar sözlükten atlanmıştır. JSON kullanıcı arayüzüne hangi alanların
sorulacağını bildirir, fakat girilen yanıtı kabul eden kod yoktur.

## 14. Ana envanter tablosu

| Alan | Kaynak | Mevcut mu? | Yapılandırılmış mı? | Birim | Güven bilgisi | Manuel doğrulama | Nihai JSON'da mı? | İlgili dosya |
|---|---|---|---|---|---|---|---|---|
| Faz tipi | Sayaç OCR'dan türetilmiş | Evet | Evet, `faz` | — | 0–100 `faz_guvenskor` | Yok | Evet | `predict_and_ocr.py` |
| Gerilim | Sayaç OCR | OCR'da evet | Hayır | V | Yalnız OCR satırı güveni | Yok | Yalnız `ocr_metinleri` | `predict_and_ocr.py`, `ocr_engine.py` |
| Frekans | Sayaç OCR | OCR'da evet | Hayır | Hz | Yalnız OCR satırı güveni | Yok | Yalnız `ocr_metinleri` | Aynı |
| Akım aralığı | Sayaç OCR | OCR'da evet | Hayır | A | Yalnız OCR satırı güveni | Yok | Yalnız `ocr_metinleri` | Aynı |
| Azami akım | Sayaç OCR | OCR'da evet | Hayır | A | Yalnız OCR satırı güveni | Yok | Yalnız `ocr_metinleri` | Aynı |
| Sayaç marka/model/tip | Sayaç OCR | OCR'da evet | Hayır | — | Yalnız OCR satırı güveni | Yok | Yalnız `ocr_metinleri` | Aynı |
| Sayaç seri no (fotoğraf) | Sayaç OCR | OCR'da olabilir | Hayır | — | Yalnız OCR satırı güveni | Yok | Yalnız `ocr_metinleri` | Aynı |
| Sayaç bulundu | YOLO | Evet | Evet, `sayac_bulundu` | — | `yolo_guveni` ayrı | Yok | Evet | `predict_and_ocr.py` |
| Fatura bulundu | YOLO + OCR | Evet | Evet, `fatura_bulundu` | — | YOLO ve OCR doğrulama skoru | İnceleme bayrağı var | Evet | `bill_predict_and_ocr.py` |
| Şirket | Fatura OCR'dan türetilmiş | Evet | Evet, `sirket` | — | 0–1 | Yok | Evet | `bill_field_extractor.py` |
| Sözleşme gücü | Fatura | Evet | Evet, `sozlesme_gucu_kw` | kW | 0–1 | İhtiyaç işareti var; giriş yok | Evet, bulunursa | Aynı |
| Çarpan | Fatura | Şablona bağlı | Evet, `carpan` | — | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Demand | Fatura | Şablona bağlı | Evet, `demand_kw` | kW | 0–1 | İhtiyaç işareti olabilir | Evet, birleşik alan varsa; değer `null` olabilir | Aynı |
| Dönem tüketimi | Fatura | Evet | Evet, `donem_tuketimi_kwh` | kWh | 0–1 | İhtiyaç işareti var; giriş yok | Evet, bulunursa | Aynı |
| Günlük ortalama | Fatura | Şablona bağlı | Evet, `gunluk_ortalama_kwh` | kWh/gün | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Tüketici grubu | Fatura | Şablona bağlı | Evet, `tuketici_grubu` | — | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Tarife | Tüketici grubundan türetilmiş | Evet | Evet, `tarife` | — | Tüketici grubu güveni | Kritik ihtiyaç işareti var; giriş yok | Evet, bulunursa | Aynı |
| Gerilim seviyesi | Tüketici grubundan türetilmiş | Kısmen | Ayrı alan değil; `tarife` parçası | — | Tarife güveni | Tarife üzerinden işaret | Birleşik stringde | Aynı |
| Tek/çok zaman | Tüketici grubundan türetilmiş | Kısmen | Ayrı alan değil; `tarife` parçası | — | Tarife güveni | Tarife üzerinden işaret | Birleşik stringde | Aynı |
| Ödenecek tutar | Fatura | Evet | Evet, `odenecek_tutar_tl` | TL | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Fatura dönemi | Fatura | Evet | Evet, `fatura_donemi` | — | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Son ödeme tarihi | Fatura | Kural mevcut | Evet, yakalanırsa | Tarih | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Sayaç seri no (fatura) | Fatura | Kural mevcut | Evet, yakalanırsa | — | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Sayaç tipi (fatura) | Fatura | Kural mevcut | Evet, yakalanırsa | — | 0–1 | İhtiyaç işareti olabilir | Evet, bulunursa | Aynı |
| Alan etiketi/ham değer/yöntem/bbox | Fatura alan kanıtı | Evet | Evet | Değişken | Alan güveniyle birlikte | Kullanıcıya kanıt olabilir; doğrulama girişi yok | `alanlar` içinde | Aynı |
| Eksik kritik alanlar | Türetilmiş | Evet | Evet | — | Eşik 0.70 politikasıyla ilişkili | Manuel ihtiyacın kaynağı | Evet | Aynı |
| Düşük güvenli alanlar | Türetilmiş | Evet | Evet | — | `<0.70` | Manuel ihtiyacın kaynağı | Evet | Aynı |
| Manuel giriş gerekli | Türetilmiş | Evet | Evet, bool | — | Eksik/düşük listelerinden | Yalnız bayrak; giriş akışı yok | Evet | Aynı |
| Araç kimliği/marka/model/varyant | Planlama JSON/Excel | Evet, bağımsız prototip | Veri dosyasında evet; API'de hayır | — | Kaynak/güven alanları var | Çalışan kullanıcı seçimi yok | Analiz JSON'unda hayır | `planning/*` |
| Araç azami AC gücü | Planlama JSON/Excel | Evet, bazı kayıtlarda | Veri dosyasında evet; API'de hayır | kW | Veri güven alanı var | Yok | Analiz JSON'unda hayır | `planning/*` |
| Araç faz/akım desteği | Planlama JSON/Excel | Evet, bazı kayıtlarda | Veri dosyasında evet; API'de hayır | A / faz | Veri güven alanı var | Yok | Analiz JSON'unda hayır | `planning/*` |
| Batarya/WLTP | Planlama JSON/Excel | Kısmen | Veri dosyasında evet; API'de hayır | kWh, km, kWh/100 km | Veri güven alanı var | Yok | Analiz JSON'unda hayır | `planning/*` |
| Şarj istasyonu güç/faz/akım/soket | Şarj istasyonu kataloğu | Hayır | Hayır | Değişken | Yok | Yok | Hayır | Tespit edilmedi |
| Dinamik yük yönetimi | Şarj istasyonu kataloğu | Hayır | Hayır | — | Yok | Yok | Hayır | Tespit edilmedi |
| Şarj istasyonu fiyat/garanti/akıllı özellikler | Şarj istasyonu kataloğu | Hayır | Hayır | Değişken | Yok | Yok | Hayır | Tespit edilmedi |
| Günlük kilometre | Kullanıcı | Hayır | Hayır | km/gün | Yok | Giriş akışı yok | Hayır | Tespit edilmedi |
| Park/şarj süresi | Kullanıcı | Hayır | Hayır | saat | Yok | Giriş akışı yok | Hayır | Tespit edilmedi |
| Bütçe | Kullanıcı | Hayır | Hayır | TL | Yok | Giriş akışı yok | Hayır | Tespit edilmedi |
| Eşzamanlı ev yükü | Kullanıcı/ölçüm | Hayır | Hayır | kW | Yok | Giriş akışı yok | Hayır | Tespit edilmedi |
| Sigorta/kablo/pano/RCD/topraklama | Kullanıcı/elektrikçi | Hayır | Hayır | Değişken | Yok | Giriş akışı yok | Hayır | Tespit edilmedi |

## Tespit edilen dokümantasyon ve kod farklılıkları

1. `MODEL_DURUMU.md`, belirsiz faz için `bilinmiyor` ifadesini kullanmaktadır;
   çalışan kodun gerçek değeri `belirsiz`dir.
2. Yöntem raporu kişisel verilerin maskelenmesini gerekli görür; çalışan API
   ham `ocr_metinleri` listesini maskelemeden döndürmektedir.
3. `API_README.md` ağırlıklı olarak fatura tespiti ve OCR'ı tarif eder; çalışan
   kod bunlara ek olarak yapılandırılmış `fatura_bilgileri` üretmektedir.
4. Dokümandaki “belge parçalama” anlatımı yalnız fatura belgesine özgü değildir;
   `ocr_engine.py`, OCR'a verilen her büyük görüntü/kırpma için parçalama yapar.
5. Dokümanlarda manuel girişten iş akışı gibi söz edilebilse de mevcut kodda
   yalnız `manuel_giris_gerekli` ve alan listesi vardır; kullanıcı değerini alan
   ve birleştiren mekanizma yoktur.

## Sonuç

Mevcut kod, karar destek sisteminin altyapı tarafı için güvenilir bir başlangıç
envanteri üretmektedir; fakat tamamlanmış bir karar destek sistemi değildir.
Faz tipi ile fatura güç/tüketim/tarife alanları programatik ve kanıtlı çıktılara
dönüşmektedir. Sayaç gerilimi ve azami akımı ise karar açısından önemli olmasına
rağmen şu anda yalnız ham OCR içindedir. Araç veri prototipi bağımsız olarak
mevcuttur; şarj istasyonu kataloğu, kullanıcı ihtiyaç girdileri ve eşleştirme
algoritması yoktur. Bu sınırlar korunarak, mevcut sistemin sunduğu veriler
olduğundan geniş gösterilmeden sonraki aşamanın girdileri tanımlanabilir.
