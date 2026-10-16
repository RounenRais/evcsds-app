# `testimagelast` sayaç ve fatura pilot değerlendirmesi

**Tarih:** 2026-10-11  
**Kapsam:** `test0`–`test9` (10 sayaç), `syctest0`–`syctest7` (8 fatura).

## Yöntem ve veri ayrımı

Görseller, API ile aynı `gorseli_hazirla` ön işlemesinden geçirilerek mevcut sayaç ve fatura analiz işlevlerinde çalıştırıldı. Sayaç fotoğraflarındaki faz ibaresi ayrıca görsel üzerinden elle okundu; faturalarda bütün alanları kapsayan çift kontrollü gerçek değer tablosu henüz yoktur. Bu nedenle aşağıdaki fatura sayıları **çıktı/doluluk** gözlemidir, alan doğruluğu oranı değildir.

Görseller, proje içindeki 1.632 görüntüyle dosya özeti ve basit algısal özet düzeyinde karşılaştırıldı; birebir veya bariz yakın kopya görülmedi. Bununla birlikte özellikle faturaların kaynak belge ve şablon kökeni doğrulanmadığından bunlara kesin biçimde **bağımsız test kümesi** denemez. Görsel dosyanın farklı olması, belgenin eğitim/geliştirme sırasında hiç görülmediğini kanıtlamaz. Bu raporda kişisel fatura metni ve ham OCR dökümü tutulmamıştır.

## Sayaç sonuçları

| Görsel | Görselde okunan faz | Sistem sonucu | Sayaç tespit güveni | Değerlendirme |
|---|---|---|---:|---|
| `test0.jpg` | trifaz | trifaz | 0,96 | Doğru |
| `test1.jpg` | trifaz | trifaz | 0,75 | Doğru |
| `test2.png` | trifaz | trifaz | 0,77 | Doğru |
| `test3.png` | trifaz | trifaz | 0,83 | Doğru |
| `test4.jpg` | trifaz | belirsiz | 0,82 | Güvenli geri çekilme; faz etiketi kaçırıldı |
| `test5.png` | monofaz | monofaz | 0,91 | Doğru |
| `test6.jpg` | monofaz | monofaz | 0,86 | Doğru |
| `test7.png` | trifaz | trifaz | 0,76 | Doğru |
| `test8.png` | trifaz | trifaz | 0,79 | Doğru |
| `test9.png` | trifaz | trifaz | 0,91 | Doğru |

Bu pilotta sayaç tespiti 10/10; faz sınıflandırması 9/10 doğru, 1/10 belirsiz ve 0/10 yanlış kesin karardır. Bu yalnızca on örnek üzerindeki gözlemdir; farklı marka, ışık ve gerçek kullanıcı dağılımı için güven aralıklı saha doğruluğu iddiası değildir. Sayaç gerilimi ve akımı henüz tüm biçimlerde yapılandırılmış KDS alanı olarak çıkarılmamaktadır.

## Fatura sonuçları ve bulunan hatalar

İlk tam taramada 8/8 görsel fatura olarak doğrulandı; üçünde tam görsel OCR geri dönüşü gerekti. İlk tarama süreleri 89–213 saniye aralığındaydı (ortanca yaklaşık 132 saniye). Alanların *dolu görünme* sayısı sözleşme gücü 6/8, dönem tüketimi 2/8, tarife 2/8 idi. Dolu olması doğruluk anlamına gelmemektedir: yanlış dolu sonuçlar tespit edildi.

| Görsel | İlk taramadaki kritik gözlem | Düzeltme sonrası gerçek görsel kontrolü |
|---|---|---|
| `syctest0.jpg` | Kritik alanlar boş; manuel giriş | Bu sürümde yeniden çalıştırılmadı |
| `syctest1.jpg` | Güç 9,04 kW, tarife dolu; tüketim boş | Bu sürümde yeniden çalıştırılmadı; alanlar tam etiketlenmedi |
| `syctest2.jpg` | Güç 5,0 kW; tüketim ve tarife boş | Bu sürümde yeniden çalıştırılmadı; görsel çok küçük |
| `syctest3.jpg` | Kritik alanlar boş; manuel giriş | Bu sürümde yeniden çalıştırılmadı; iki sayfalı küçük görüntü |
| `syctest4.jpg` | Yanlış 24 kW: birleşik alan yanındaki `024` tek başına güç sayıldı | Son doğrudan görsel taramasında birleşik alandan 6,408 kW çıkarıldı; dönem tüketimi hâlâ manuel doğrulamada |
| `syctest5.png` | Yanlış 40 kW: etiket içindeki 6,09 yerine komşu kodun başı alındı | Görselde açıkça yazan 6,09 kW çıkarıldı; tüketim/tarife manuel |
| `syctest6.png` | Yanlış 40 kW ve düşük kademe satırından eksik 232 kWh | Güç 6,09 kW; toplam tüketim `null` ve manuel |
| `syctest7.jpg` | İlk taramada yanlış 1 kWh; sayı ayrıştırması düzeltildikten sonra bir endeks 206 kWh olarak seçildi | Güç, tüketim ve tarife `null`; manuel doğrulama istendi |

`syctest4`–`syctest6` ilk korumalar eklendikten sonra, `syctest7` ise son sayı ve tablo korumasından sonra aynı ön işleme/OCR zincirinde yeniden çalıştırıldı. Daha sonra `syctest4` ham görseli doğrudan `fatura_analiz_et` ile bir kez daha çalıştırıldı: OCR başlığı `'arpan/Demand/Anl.Gücü`, ham değeri `1,000/-/6.408` olarak okudu ve yeni etiket toleransı 6,408 kW üretti. Bu son tarama API ön işlemesinden geçmediği için onunla birebir eşdeğer sayılmamalıdır. `syctest5`–`syctest6` son sayı ayrıştırma değişikliğinden sonra, `syctest0`–`syctest3` de yeni kurallarla tekrar koşulmadı. Bu nedenle **son sürüm için bütün sekiz faturayı kapsayan yeni bir başarı/doluluk yüzdesi verilmemektedir**.

Ardından aynı `syctest4` görseli API'nin `gorseli_hazirla` ön işlemiyle tekrar çalıştırıldı ve yine 6,408 kW bulundu. Bu tek örnek, diğer faturalara genelleme değildir.

### Kullanıcı etiketleriyle ilk API ön işlemli kontrol (düzeltme öncesi)

2026-10-11 tarihinde kullanıcının görselden okuduğu altı güç ve dört tarife değeri `planning/FATURA_SAHA_DOGRULAMA_SABLONU.csv` dosyasına işlendi. Bu etiketler henüz ikinci kişiyle doğrulanmadı; görsellerin eğitim/geliştirme kaynaklarından bağımsızlığı da bilinmiyor. Günlük tüketimlerin yıl karşılaştırmaları dönem toplamı olarak etiketlenmedi.

| Görsel | Fatura tespiti | Sözleşme gücü | Tarife |
|---|---|---|---|
| `syctest0` | Doğru | Kaçırıldı | Kaçırıldı |
| `syctest1` | Doğru | Doğru | Etiketle uyuşmayan dolu sonuç |
| `syctest2` | Doğru | Kaçırıldı | Kaçırıldı |
| `syctest4` | Doğru | Doğru | Doğru |
| `syctest5` | Doğru | Doğru | Etiket yok, puanlanmadı |
| `syctest6` | Doğru | Doğru | Etiket yok, puanlanmadı |

Bu altı örnekte fatura tespiti 6/6, güç 4 doğru ve 2 kaçırma, tarife 1 doğru, 1 uyuşmayan dolu sonuç ve 2 kaçırma verdi. Dönem tüketimi için doğrulanmış etiket bulunmadığından başarı hesaplanmadı. Aynı API ön işlemesiyle ölçülen analiz süresinin medyanı yaklaşık 177 saniye, bu altı örneğin en yavaşı yaklaşık 247 saniyedir. Bunlar yalnız hata ayıklama sayılarıdır; bağımsız saha performansı ya da yayın onayı değildir.

### Hedefli OCR ve alan eşleştirme düzeltmelerinden sonraki kontrol

İlk kontrolde sayaç/fatura nesne tespiti değil, fatura üzerindeki metnin okunması ve okunan etiketin değere bağlanması sorunlu bulundu. Birleşik `Çarpan/Demand/Anl. Gücü` başlığındaki OCR boşluklarına tolerans eklendi; bozuk üçlü değerde yalnız görülen başlığın yakınındaki satır bir kez büyütülerek tekrar OCR'dan geçirildi. Ayrı kutulara bölünmüş `Tüketici Grubu` etiketi ve değeri aynı satırda eşleştirildi; `A G` kısaltması alçak gerilim olarak tanındı. Başlık/üçlü değer kanıtı olmadan güç üretilmiyor.

| Görsel | Fatura tespiti | Güç | Tarife | Dönem toplamı |
|---|---|---|---|---|
| `syctest0` | Doğru | 7,13 kW, kullanıcı etiketiyle uyumlu | `mesken_tek_zamanli_alcak_gerilim`, uyumlu | `null` |
| `syctest1` | Doğru | 9,04 kW, uyumlu | `mesken_tek_zamanli_alcak_gerilim`, uyumlu | `null` |
| `syctest2` | Doğru | 5,01 kW, uyumlu | `null`; küçük görselde tarife metni OCR ile okunamadı | `null` |
| `syctest4` | Doğru | 6,408 kW, uyumlu | `mesken_tek_zamanli_alcak_gerilim`, uyumlu | `null` |
| `syctest5` | Doğru | 6,09 kW, uyumlu | Etiket yok; `null` | `null` |
| `syctest6` | Doğru | 6,09 kW, uyumlu | Etiket yok; `null` | `null` |

Altı görsel aynı son kod sürümü ve API görüntü ön işlemesiyle yeniden koşuldu: fatura tespiti 6/6, kullanıcı etiketine göre güç 6/6, etiketli dört tarifeden 3 doğru ve 1 boş. Dönem toplamları için doğrulanmış etiket bulunmadığından doğruluk hesaplanmadı; bu altı çıktıda alan boş kaldı. Analiz süresinin medyanı yaklaşık 33 saniye, bu koşudaki p95 değeri yaklaşık 48 saniyedir (aynı makinede önceden yüklenmiş model dosyalarıyla); farklı donanım için vaat değildir. Kullanıcı tarafından okunan etiketler ikinci bir okuyucuyla doğrulanmadı ve hiçbir örneğin bağımsız test kaynağı olduğu kanıtlanmadı. Dolayısıyla bunlar yalnız geliştirme sonuçlarıdır, herkese açık kullanımda genel doğruluk garantisi vermez.

Görsel incelemede `syctest0` için `Tek Zamanlı → Fark` alanında 770,654 kWh, `syctest1` için aynı alanda 195,057 kWh **dönem toplamı adayı** görüldü; `syctest1` tutarı tüketim tablosunda da tekrar ediyor. Kullanıcının verdiği yıl bazlı günlük ortalama sayılarından farklı alanlardır. İlk kullanıcı notuyla `syctest1` dönem toplamı konusunda uyuşmazlık bulunduğundan bu iki aday değerlendirme etiketine eklenmedi; ikinci okuyucuyla teyit edilmelidir.

## Yapılan sınırlı güvenlik düzeltmeleri

`bill_field_extractor.py` içinde birleşik Çarpan/Demand/Güç etiketi, üçlü değer okunamazsa tek bir komşu sayıdan güç üretmiyor. OCR baştaki `Ç` harfini düşürüp `'arpan` okursa, yalnızca `Demand` ve `Güç` aynı etikette ve geçerli üçlü değer yakınında bulunduğunda eşleşme kabul ediliyor. Tek OCR kutusundaki açık `Sözleşme Gücü: 6,09` ifadesi doğrudan değerlendiriliyor; tesisat/kayıt kodları saf sayısal güç adayı sayılmıyor. Reaktif tüketim, kademe numarası veya tek kademe satırı toplam dönem tüketimi olarak aktarılmıyor. Beş basamaklı sayıların ilk üç basamakta kesilmesi giderildi. Çok sütunlu endeks tablosunda doğru fark sütunu güvenilir biçimde belirlenemiyorsa tüketim boş bırakılıyor. KDS V1.1'e göre tüketim/tarife eksikleri isteğe bağlı doğrulamaya ayrılıyor. Alan çıkarma, değerlendirme aracı ve KDS ev girdi eşlemesi için 26 otomatik test geçmiştir.

Bu düzeltmeler belirlenen hata türlerini hedefler; **fatura alan çıkarma doğruluğunun genelleştiğini kanıtlamaz**. Güven puanları kalibre edilmiş olasılık değildir. Dört mevcut fatura olmayan geliştirme görseli önceki kontrolde doğru reddedildi; yeni düzeltmelerin ardından ayrı bir negatif tarama yapılmadı ve çeşitli bağımsız negatif örnekler hâlâ eksiktir. Mevcut `home` girdisi eksik veya düşük güvenli alanları manuel doğrulamaya yönlendirse de başka yüksek güvenli yanlış eşleşmelerin kalmadığı henüz gösterilmemiştir.

## Yayın kararı ve sıradaki doğrulama

**Karar: herkese açık, otomatik KDS girdisi olarak yayımlanmaya hazır değil.** Mevcut yapı kontrollü prototip/beta için değerlendirilebilir; kritik fatura değerleri kullanıcıya gösterilip doğrulatılmalıdır. Faz belirsizse kullanıcı girdisi alınmalıdır. Tesisatın kurulum uygunluğu fotoğraflarla kanıtlanamaz.

Sonraki adım, bu sekiz fatura dâhil her belgenin gerçekten yeni olup olmadığını kaynak belge kimliğiyle doğrulamak ve sözleşme gücü, dönem tüketimi, tarife için ikinci okuyucuyla kontrol edilmiş gerçek değer tablosu oluşturmaktır. Ardından yeni sürüm kalan iki faturada ve fatura olmayan/bağımsız negatif görsellerde çalıştırılmalı; doğru dolu, yanlış dolu, boş/manual oranları ve p50/p95 süreleri ayrı raporlanmalıdır. OCR gecikmesi ve küçük/çok sayfalı belge başarısı iyileştirilmeden genel erişim hedeflenmemelidir.
