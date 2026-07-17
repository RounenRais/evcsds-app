# Elektrik Sayacı ve Fatura Görsellerinden Konut Elektrik Altyapısı Bilgilerinin Çıkarılması: Açıklanabilir Hibrit Bir Görüntü İşleme Yaklaşımı

## Öz

Elektrikli araçların konutlarda güvenli ve verimli biçimde şarj edilebilmesi,
önerilecek şarj istasyonunun aracın özellikleri kadar mevcut elektrik
altyapısıyla da uyumlu olmasını gerektirmektedir. Bu çalışmada, kullanıcı
tarafından sağlanan elektrik sayacı ve elektrik faturası görsellerinden karar
destek sisteminde kullanılabilecek altyapı bilgilerinin otomatik olarak
çıkarılması amaçlanmıştır. Sayaç ve fatura bölgelerinin belirlenmesinde transfer
öğrenme uygulanmış YOLO11n nesne tespit modelleri; yazıların okunmasında
PaddleOCR; OCR kaynaklı yazım farklılıklarının giderilmesinde Unicode
normalizasyonu ve RapidFuzz; metinlerin anlamsal alanlara dönüştürülmesinde ise
koordinat, tablo, birim ve bağlam kurallarını birleştiren açıklanabilir bir alan
çıkarma motoru kullanılmıştır.

Fatura görsellerinin şirket ve dönemlere göre önemli ölçüde değişmesi, sınırlı
sayıda özgün fatura bulunması ve eğitim görsellerindeki fatura kutularının
çoğunlukla görüntünün tamamını kaplaması nedeniyle yalnızca nesne tespitine
dayanan yaklaşımın gerçek kullanıcı fotoğraflarında yeterli olmadığı
görülmüştür. Bu nedenle düşük güvenli tespitlerde bütün görüntüyü parçalara
ayıran OCR geri dönüşü, etiket eş anlamlıları, uzamsal etiket-değer eşleştirmesi,
birim ve değer aralığı doğrulaması ile yalnızca belirsiz alanlar için manuel
girdi isteme mekanizması geliştirilmiştir. Gerçek Enerjisa test faturasında
`Çarpan/Demand/Anl. Gücü` etiketiyle ilişkili `1,000/-/3,000` değeri
çözümlenerek sözleşme gücü 3,0 kW olarak çıkarılmış; dönem tüketimi 246,186 kWh,
günlük ortalama tüketim 8,206 kWh/gün ve tarife sınıfı da standart alanlara
dönüştürülmüştür. Çalışma, sınırlı veri koşullarında yeniden model eğitmek yerine
görüntü modeli, OCR ve açıklanabilir kuralların birlikte kullanılmasının daha
uygulanabilir ve denetlenebilir bir çözüm sunduğunu göstermektedir.

**Anahtar kelimeler:** elektrikli araç, ev tipi şarj istasyonu, elektrik sayacı,
elektrik faturası, YOLO11, PaddleOCR, RapidFuzz, anahtar bilgi çıkarımı, karar
destek sistemi.

## 1. Giriş

Ev tipi elektrikli araç şarj istasyonlarının güç seviyeleri, konutun elektrik
altyapısının sağlayabileceği kapasiteyle sınırlandırılmaktadır. Tek fazlı veya üç
fazlı besleme, sayaç üzerinde belirtilen gerilim ve azami akım değeri, faturada
yer alan sözleşme gücü ve tüketim profili karar destek sürecinde birlikte
değerlendirilmelidir. Bu bilgilerin kullanıcı tarafından eksiksiz ve teknik
terimlere uygun biçimde girilmesini beklemek kullanım hatalarına yol açabilir.
Bu nedenle çalışma kapsamında sayaç ve fatura fotoğraflarından yarı otomatik
altyapı bilgisi çıkaran bir sistem geliştirilmiştir.

Çalışmanın temel araştırma sorusu şöyledir: **Sınırlı ve heterojen fatura verisi
koşullarında, farklı şirket ve şablonlardaki altyapı bilgileri yeniden büyük bir
model eğitilmeden güvenilir ve açıklanabilir biçimde nasıl çıkarılabilir?** Bu
soru doğrultusunda yalnızca OCR metnini döndüren bir sistem yerine, her sonucun
hangi etiketten ve hangi görüntü bölgesinden üretildiğini gösteren, belirsizlik
durumunda kullanıcıya başvuran hibrit bir mimari benimsenmiştir.

Geliştirilen sistem elektrik tesisatı için resmi uygunluk veya kurulum onayı
vermemektedir. Kablo kesiti, ana sigorta, kaçak akım koruması, pano kapasitesi,
topraklama ve tesisatın fiziksel durumu fotoğraflardan kesin olarak
doğrulanamayacağından nihai kurulum öncesinde yetkili elektrikçi incelemesi
zorunludur. Çıktılar, şarj istasyonu seçimini destekleyen ön değerlendirme
verileridir.

## 2. Veri Setleri ve Veri Hazırlama

### 2.1. Elektrik sayacı veri seti

Sayaç tespit veri seti Roboflow ortamında işaretlenmiş ve YOLO biçiminde dışa
aktarılmıştır. Dışa aktarılan veri setinde tek sınıf (`electric-meter-detection`)
bulunmaktadır. Proje klasöründeki son dağılım Tablo 1'de verilmiştir.

**Tablo 1. Sayaç veri setinin dağılımı**

| Alt küme | Görüntü sayısı |
|---|---:|
| Eğitim | 249 |
| Doğrulama | 17 |
| Test | 10 |
| Toplam | 276 |

Sayaç görsellerinde farklı marka, açı, ışık ve arka plan koşullarının bulunması,
modelin yalnızca belirli bir sayaç tasarımına bağlı kalmaması açısından önemlidir.
Veri seti tanımında CC BY 4.0 lisans bilgisi bulunmaktadır.

### 2.2. Elektrik faturası veri seti

Fatura veri kaynağı; Google Görseller, forum gönderileri ve videolardan alınan
kareler dâhil olmak üzere farklı şirket ve yılları temsil eden yaklaşık 70 özgün
faturadan oluşturulmuştur. İnternette okunabilir, farklı tasarımları temsil eden
ve eğitim amacıyla kullanılabilecek fatura sayısının sınırlı olması, çalışmanın
başlıca veri kısıtıdır.

Roboflow dışa aktarımında dönüşüm ve veri artırma sonucunda tek sınıflı
(`electricity-bill`) veri setinde aşağıdaki sayılar elde edilmiştir:

**Tablo 2. Fatura veri setinin dışa aktarım dağılımı**

| Alt küme | Dışa aktarılan görüntü sayısı |
|---|---:|
| Eğitim | 484 |
| Doğrulama | 56 |
| Test | 52 |
| Toplam | 592 |

Buradaki 592 sayısı 592 bağımsız özgün fatura anlamına gelmemektedir; yaklaşık
70 kaynak görselin dönüşüm ve artırılmış türevlerini de kapsamaktadır. Bu ayrım,
model metriğinin yorumlanmasında önemlidir. Aynı kaynak faturanın türevlerinin
farklı veri alt kümelerine dağılması hâlinde veri sızıntısı ve olduğundan yüksek
başarı riski oluşabileceğinden gelecekte özgün belge kimliğine göre grup tabanlı
veri bölme yapılması önerilmektedir.

### 2.3. Etik ve kişisel verilerin korunması

Faturalar ad-soyad, adres, TCKN, müşteri numarası ve tesisat numarası gibi kişisel
veriler içerebilir. Bu alanlar şarj istasyonu önerisi için gerekli değildir.
Dolayısıyla rapor, sunum ve ileride oluşturulacak veri setlerinde söz konusu
alanların maskelenmesi; kullanıcı verilerinin yalnızca açık rıza, amaçla
sınırlılık ve güvenli saklama ilkeleriyle işlenmesi gerekmektedir. Sistem
çıktısında karar desteği için zorunlu olmayan kişisel alanların tutulmaması veri
minimizasyonu yaklaşımının bir gereğidir.

## 3. Kullanılan Teknolojiler ve Seçilme Gerekçeleri

Teknoloji seçimi yalnızca doğruluk hedefiyle değil; sınırlı veri, açıklanabilirlik,
yerel çalışabilme, tekrarlanabilirlik ve prototipin mevcut donanımda
çalıştırılabilmesi ölçütleriyle yapılmıştır.

### 3.1. Python

Sistem Python programlama diliyle geliştirilmiştir. Python; PyTorch,
Ultralytics, OpenCV, PaddleOCR ve RapidFuzz kütüphanelerinin aynı iş akışında
kullanılmasına olanak vermesi, deneylerin hızlı kurulabilmesi ve araştırma
kodunun okunabilir olması nedeniyle seçilmiştir. Modüler yapı sayesinde sayaç
tespiti, fatura tespiti, OCR ve alan çıkarma bileşenleri birbirinden bağımsız
olarak test edilebilmektedir.

### 3.2. Ultralytics YOLO11n

Sayaç ve fatura bölgelerinin tespitinde Ultralytics YOLO11 ailesinin nano modeli
olan YOLO11n kullanılmıştır. YOLO tek aşamalı nesne tespit yaklaşımı sayesinde
nesne konumu ve sınıf güvenini tek çıkarım sürecinde üretmektedir. Nano sürüm;
daha büyük modellere göre daha düşük hesaplama ve bellek gereksinimine sahip
olduğu, sınırlı veri ve tek sınıflı problem için yeterli başlangıç kapasitesi
sunduğu ve gerçek zamanlı kullanıma daha uygun olduğu için tercih edilmiştir [4].

Model sıfırdan eğitilmemiş, önceden eğitilmiş `yolo11n.pt` ağırlıklarıyla
transfer öğrenme uygulanmıştır. Transfer öğrenme, sınırlı proje verisiyle genel
görsel özelliklerin yeniden öğrenilmesi ihtiyacını azaltmaktadır. Ultralytics
eğitim altyapısı; veri artırma, erken durdurma, doğrulama metrikleri, ağırlık
kaydı ve CUDA/CPU cihaz seçimini ortak bir arayüzde sağlaması nedeniyle
kullanılmıştır.

### 3.3. PyTorch ve CUDA

YOLO modellerinin eğitimi ve çıkarımı PyTorch üzerinde gerçekleştirilmiştir.
PyTorch'un dinamik ve Python ile bütünleşik yürütme yapısı deneylerin
izlenmesini, hata ayıklamayı ve GPU hızlandırmasını kolaylaştırmaktadır. Fatura
modeli eğitim kaydında NVIDIA GPU (`device=0`) kullanılmıştır. Güncel çıkarım
kodunda CUDA kullanılabilir olduğunda sayaç ve fatura YOLO modelleri NVIDIA
GeForce RTX 5050 Laptop GPU üzerinde, aksi durumda CPU üzerinde çalışmaktadır.
PyTorch'un Pythonik yürütme ve donanım hızlandırma yaklaşımı literatürde ayrıntılı
olarak açıklanmıştır [1].

Sayaç modelinin mevcut eğitim kaydı CPU üzerinde gerçekleştirilmiştir. OCR
bileşeni ise Windows ortamında PaddlePaddle GPU/cuDNN ikili uyumsuzluğu
gözlendiği için kararlı çalışma öncelenerek CPU üzerinde çalıştırılmıştır. Bu
tercih doğruluktan çok dağıtım kararlılığına yöneliktir; büyük faturalarda işlem
süresini artırması çalışmanın sınırlılıklarından biridir.

### 3.4. Roboflow

Roboflow; görsellerin sınıf kutularıyla işaretlenmesi, veri seti sürümlemesi,
eğitim/doğrulama/test klasörlerinin oluşturulması ve YOLO biçiminde dışa aktarım
için kullanılmıştır. Bu tercih, farklı kaynaklardan toplanan görsellerde ortak
etiket biçiminin korunmasını ve deneylerin aynı veri tanımıyla yeniden
çalıştırılmasını kolaylaştırmıştır. Bununla birlikte veri artırılmış türevlerin
bağımsız örnek gibi yorumlanmaması gerektiği raporda özellikle dikkate
alınmıştır.

### 3.5. OpenCV ve NumPy

OpenCV; görüntünün okunması, YOLO kutusuna göre kırpılması, kutuya güvenlik payı
eklenmesi ve OCR'a uygun görüntü matrisinin hazırlanması için kullanılmıştır.
NumPy, görüntülerin matris temsili ve parça işlemlerinin temel veri yapısını
sağlamaktadır. OpenCV'nin tercih edilme nedeni, nesne tespiti ile OCR arasında
düşük ek yükle çalışan, yaygın ve denetlenebilir bir görüntü işleme katmanı
sunmasıdır.

### 3.6. Pillow

Kullanıcıdan gelebilecek JPEG, PNG ve WebP dosyalarının gerçek biçimini
doğrulamak, EXIF yön bilgisini uygulamak, yüksek çözünürlüklü görselleri en-boy
oranını koruyarak küçültmek ve görüntüleri ortak RGB/JPEG biçimine dönüştürmek
için Pillow kullanılmıştır. Dosya uzantısına güvenmek yerine görüntü içeriğinin
doğrulanması, bozuk veya beklenmeyen dosyaların görüntü işleme zincirine
girmesini engellemektedir.

### 3.7. PaddleOCR ve PP-OCRv5

Sayaç ve fatura üzerindeki metinlerin tespit ve tanınmasında PaddleOCR
kullanılmıştır. Yapılandırmada `PP-OCRv5_mobile_det` metin tespit modeli ve Latin
karakterler için `latin_PP-OCRv5_mobile_rec` tanıma modeli bulunmaktadır.
PaddleOCR'ın tercih edilme nedenleri şunlardır:

1. Metin içeriğiyle birlikte metin kutusu koordinatlarını üretmesi,
2. Eğik, küçük ve farklı boyuttaki metinleri tespit edebilmesi,
3. Önceden eğitilmiş modellerle sınırlı proje verisinde yeniden OCR eğitimi
   gerektirmemesi,
4. Yerel çalışarak fatura verilerinin haricî bir servise gönderilmesini
   gerektirmemesi,
5. Mobil model seçeneğiyle doğruluk-hesaplama maliyeti arasında uygulanabilir bir
   denge sunmasıdır.

PP-OCR ailesi hafif ve uygulamaya dönük OCR yaklaşımı olarak geliştirilmiş [2],
PP-OCRv5 ise PaddleOCR 3.0 kapsamında çok dilli metin tanıma çözümü olarak
sunulmuştur [3].

Büyük faturalar 1800 × 1800 piksel parçalara, 120 piksel örtüşmeyle ayrılmıştır.
Bu yöntem, OCR motorunun maksimum kenar sınırında bütün belgenin aşırı
küçültülerek küçük yazıların kaybedilmesini azaltmaktadır. Her parçanın yerel
koordinatları ana görüntü koordinatlarına taşınmakta; örtüşen parçalarda aynı
konumda tekrar okunan metinler kesişim-birleşim oranıyla tekilleştirilmektedir.

### 3.8. RapidFuzz

OCR çıktılarında `Sözleşme Gücü` ifadesi `Sozlesme Gucu`, `Sözlesme Gücü` veya
benzeri küçük karakter hatalarıyla okunabilmektedir. Katı metin eşitliği bu
etiketleri kaçıracağından RapidFuzz kütüphanesinin `fuzz.partial_ratio` yöntemi
kullanılmıştır. `partial_ratio`, daha kısa etiketin uzun OCR metni içindeki en
uygun hizalamasını aradığı için `Fatura Dönemi/Tarihi/Saati` gibi birleşik
başlıklarda da yararlıdır [5].

Etiket adaylığı için uygulamada 0,72 düzeyinde normalize edilmiş benzerlik eşiği
kullanılmıştır. Ancak RapidFuzz sonucu tek başına nihai karar değildir. Genel
etiket-değer puanında etiket benzerliği, uzamsal yakınlık ve OCR güveni birlikte
değerlendirilmiştir. Bu puan uygulamaya özgü sezgisel bir güven göstergesidir;
istatistiksel olarak kalibre edilmiş olasılık şeklinde yorumlanmamalıdır.

### 3.9. Düzenli ifadeler ve Unicode normalizasyonu

Python `re` ve `unicodedata` modülleri; Türkçe karakterlerin normalize edilmesi,
tarih, sayı, `kW`, `kWh`, `TL` ve birleşik değer biçimlerinin ayrıştırılması için
kullanılmıştır. Düzenli ifadeler tek başına kullanılmamış, yalnızca doğru etiket
ve konum bağlamında aday değeri biçimsel olarak doğrulamak amacıyla
uygulanmıştır. Bu yaklaşım açıklanabilirlik ve tekrarlanabilirlik sağlamaktadır.

### 3.10. JSON ve otomatik test altyapısı

Çıktılar karar destek sisteminin kullanabileceği standart JSON yapısına
dönüştürülmüştür. Python `unittest` altyapısıyla birleşik güç alanı, ayrı yazılmış
sözleşme gücü, yanlış dönem eşleşmesi, endeks tablosu ve günlük ortalama
önceliğini kapsayan regresyon testleri hazırlanmıştır. Böylece yeni bir şirket
veya etiket kuralı eklenirken mevcut davranışların bozulup bozulmadığı otomatik
olarak denetlenebilmektedir.

## 4. Önerilen Sistem Mimarisi

Sistem iki görüntü kanalını ortak karar destek verisine dönüştürmektedir:

```text
Sayaç görseli ──► YOLO11n sayaç tespiti ──► kırpma ──► PaddleOCR
                                                    └─► faz sınıflandırma

Fatura görseli ─► YOLO11n fatura tespiti ──► OCR doğrulama
                         │ düşük güven
                         └─► tam görüntü parçalı OCR
                                  └─► şirket/etiket tanıma
                                      └─► konumsal alan çıkarma
                                          └─► birim ve mantık kontrolü

Sayaç sonucu + fatura sonucu ──► elektrik altyapısı karar destek girdisi
```

YOLO, PaddleOCR ve alan çıkarma bileşenlerinin ayrılması, bir bileşenin hatasının
doğrudan nihai karara dönüşmesini engellemektedir. Özellikle fatura YOLO modeli
güvenilir kutu üretemediğinde OCR tabanlı doğrulama devreye girmektedir.

## 5. Sayaç Görseli Analiz Yöntemi

### 5.1. Sayaç tespiti

Sayaç görüntüsü YOLO11n tabanlı tek sınıflı modelle işlenmektedir. Çıkarımda
güven eşiği 0,50 olarak belirlenmiş, birden fazla kutu oluşması hâlinde en yüksek
güvenli kutu seçilmiştir. Metinlerin kutu kenarında kesilmesini azaltmak için
tespit kutusuna 60 piksel güvenlik payı eklenmiş ve bu bölge OCR'a verilmiştir.

### 5.2. Sayaç metinlerinin okunması ve faz çıkarımı

OCR sonucunda sayaç markası, seri/tip bilgisi, standartlar, gerilim ve akım
işaretleri gibi metinler elde edilmektedir. Faz tipi için öncelikle açık ve
yüksek güvenilirlikteki örüntüler aranmıştır:

- `3 FAZ`, `TRİFAZ`, `3P`, `3×230/400 V` → üç faz,
- `1 FAZ`, `MONOFAZ`, `1P` → tek faz.

Açık örüntü bulunamazsa RapidFuzz ile `1 FAZLI` ve `3 FAZLI` ifadelerine
benzerlik hesaplanmaktadır. En yüksek benzerliğin en az 75 olması ve iki aday
arasında en az 8 puan fark bulunması koşulu aranır. Koşullar sağlanmazsa sistem
kesin olmayan bir sınıf üretmek yerine `belirsiz` döndürür.

Mevcut uygulamada faz tipi standart ve yapılandırılmış alan olarak
çıkarılmaktadır. Gerilim (`3×230/400 V`) ve akım (`0,25–5(100) A`) bilgileri test
sayacında OCR kanıtı olarak başarıyla okunmuştur; ancak farklı sayaç yazımlarını
kapsayan standart gerilim/akım ayrıştırıcısının ayrıca tamamlanması gerekir. Bu
ayrım, prototipin mevcut yeteneğinin olduğundan geniş gösterilmemesi için
önemlidir.

## 6. Fatura Görseli Analiz Yöntemi

### 6.1. Fatura tespiti ve OCR ile doğrulama

Fatura YOLO modeli 0,25 alt tespit eşiğiyle aday üretmekte, fakat yalnızca 0,50
ve üzerindeki kutular güvenilir kabul edilmektedir. Güvenilir kutu OCR'a verilir;
OCR metninde `Fatura`, `Sözleşme`, `Tesisat`, `Müşteri`, `Tüketim`, `Ödenecek`,
`kWh` ve `Son Ödeme` anahtarlarından en az ikisinin bulunması beklenir.

YOLO güveni düşükse veya kırpılan bölgede yeterli fatura kanıtı yoksa yanlış
kutuyla devam edilmez. Tüm görsel parçalara ayrılarak OCR çalıştırılır. Bu geri
dönüş hesaplama açısından daha pahalıdır, ancak yanlış arka plan bölgesinden
altyapı değeri çıkarma riskini azaltmaktadır.

### 6.2. Koordinatlı OCR ve satır oluşturma

Her OCR kaydı metin, OCR güveni ve sınırlayıcı kutuyla saklanır. Yakın dikey
merkezlere sahip metinler soldan sağa gruplanarak satır adayları oluşturulur.
Bu sayede OCR'ın ayrı kutulara böldüğü `Çarpan`, `Demand` ve `Anl. Gücü` gibi
başlıkların ortak bağlamda değerlendirilmesi mümkün olur.

### 6.3. Şirket ve etiket sözlüğü

Enerjisa, CK Enerji, Gediz, Aydem, Sepaş, Uludağ/Limak, Dicle ve Akedaş için OCR
metni içinde şirket ipuçları aranmıştır. Şirket tanıma, uygun özel kuralın
seçimini desteklemekle birlikte sistem yalnızca bilinen şirketlere bağlı
değildir. Genel etiket sözlüğü aşağıdaki eş anlamlıları ortak alanlara bağlar:

**Tablo 3. Standart fatura alanları ve örnek etiket eş anlamlıları**

| Standart alan | Örnek etiketler |
|---|---|
| `sozlesme_gucu_kw` | Sözleşme Gücü, Anlaşma Gücü, Anl. Gücü, Abonelik Gücü |
| `donem_tuketimi_kwh` | Dönem Tüketimi, Fatura Tüketimi, Aktif Tüketim, Tek Zaman Endeks |
| `tuketici_grubu` | Tüketici Grubu, Abone Grubu, Tarife Grubu |
| `odenecek_tutar_tl` | Ödenecek Tutar, Ödenecek |
| `fatura_donemi` | Fatura Dönemi |

### 6.4. Etiket-değer eşleştirmesi

Bir sayı yalnızca biçimi nedeniyle bir alana atanmaz. Aday etiketin sağında,
altında veya aynı tablo satırında yer alması; OCR güveni; RapidFuzz benzerliği;
birimi ve değer aralığı birlikte değerlendirilir. Genel eşleştirme puanında
etiket benzerliği %42, uzamsal yakınlık %38 ve OCR güveni %20 ağırlıkla
birleştirilmiştir. Bu oranlar mevcut geliştirme örnekleri üzerinde belirlenmiş
sezgisel tasarım parametreleridir ve daha geniş etiketli doğrulama kümesinde
kalibre edilmelidir.

### 6.5. Birleşik sözleşme gücü alanı

Enerjisa test faturasında aşağıdaki yapı bulunmaktadır:

```text
Çarpan / Demand / Anl. Gücü
1,000 / - / 3,000
```

Başlık ve değerlerin sıralı ilişkisi kullanılarak çıktı şu biçime
dönüştürülmüştür:

```json
{
  "carpan": 1.0,
  "demand_kw": null,
  "sozlesme_gucu_kw": 3.0
}
```

Bu kural yalnızca `Çarpan`, `Demand` ve `Güç` ifadelerini birlikte içeren yakın
etiket kanıtı varsa uygulanmaktadır. Böylece faturadaki herhangi bir üçlü sayı
dizisinin son elemanının yanlışlıkla sözleşme gücü kabul edilmesi önlenmiştir.

### 6.6. Tablo, birim ve bağlam doğrulaması

İlk geliştirme testinde `Tek Zaman (Endeks)` satırının üstündeki `30` okuma günü
dönem tüketimi olarak seçilmiştir. Dikey merkez ve satır farkı koşulları
sıkılaştırılarak fark sütunundaki `246,186` değeri seçilmiştir. Benzer biçimde
yıllık günlük ortalama `7,706`, fatura ortalaması `8,206` yerine seçildiğinde
`Fatura Ort. Tüketim` etiketi genel `Günlük Ortalama` etiketinden daha yüksek
önceliğe alınmış; `20.04.2026` gibi tarih adayları tüketim değerlerinden
çıkarılmıştır.

`kW` güç, `kWh` enerji ve `TL` para birimi olarak ayrı değerlendirilir. `kWh`
bağlamındaki değer sözleşme gücü yapılamaz. Konut sözleşme gücü için 0,5–100 kW
uygulama kontrol aralığı kullanılmıştır. Bu aralık fiziksel bir standart veya
mevzuat sınırı değil, açıkça hatalı OCR adaylarını elemek amacıyla kullanılan
prototip doğrulama aralığıdır.

### 6.7. Güven ve manuel giriş politikası

Her alan için değer, birim, güven, eşleşen etiket, ham OCR değeri, çıkarma yöntemi
ve görüntü kutusu kaydedilir. Sözleşme gücü, dönem tüketimi veya tarife
bulunamadığında ya da alan güveni 0,70'in altında kaldığında sistem değeri
uydurmaz. `manuel_giris_gerekli` ve `manuel_giris_alanlari` alanlarıyla yalnızca
eksik bilginin kullanıcıdan alınması sağlanır.

Bu yaklaşım, tam otomasyon oranını artırmak uğruna yanlış altyapı verisi üretmek
yerine güvenli geri çekilme ilkesini benimsemektedir.

## 7. Model Eğitimi ve Deneysel Kurulum

Her iki nesne tespit modelinde başlangıç ağırlığı YOLO11n, giriş çözünürlüğü
640 piksel, mini-yığın büyüklüğü 8 ve hedef eğitim süresi 100 epoch olarak
belirlenmiştir. Önceden eğitilmiş ağırlıklar, otomatik eniyileyici seçimi, veri
artırma ve 20 epoch sabır değerine sahip erken durdurma kullanılmıştır.

**Tablo 4. Sayaç ve fatura modellerinin eğitim yapılandırması**

| Parametre | Sayaç modeli | Fatura modeli |
|---|---|---|
| Başlangıç modeli | YOLO11n | YOLO11n |
| Görüntü boyutu | 640 | 640 |
| Batch | 8 | 8 |
| Hedef epoch | 100 | 100 |
| Kayıtlı son epoch | 66 | 41 |
| Erken durdurma sabrı | 20 | 20 |
| Önceden eğitilmiş ağırlık | Evet | Evet |
| Deterministik çalışma | Evet | Evet |
| Eğitim cihazı | CPU | CUDA GPU |
| Rastgelelik tohumu | 0 | 42 |

Eğitim kayıtlarındaki en yüksek doğrulama değerleri Tablo 5'te verilmiştir.
mAP@0.50 ve mAP@0.50:0.95 maksimumlarının farklı epochlarda oluşabileceği göz
önünde bulundurularak bunlar ayrı tanısal maksimumlar olarak raporlanmıştır.

**Tablo 5. Eğitim kayıtlarında gözlenen en yüksek doğrulama metrikleri**

| Model | En yüksek mAP@0.50 | En yüksek mAP@0.50:0.95 |
|---|---:|---:|
| Sayaç tespiti | 0,9950 | 0,7885 |
| Fatura tespiti | 0,9834 | 0,8065 |

Bu sonuçlar mevcut doğrulama dağılımındaki kutu tespit başarısını ifade eder;
bağımsız saha başarısı veya fatura içindeki alanların doğru çıkarılma oranı
değildir.

## 8. Bulgular

### 8.1. Sayaç testi

`sayac001.jpg` gerçek test görselinde sayaç 0,93 YOLO güveniyle tespit edilmiştir.
OCR 26 metin bölgesi üretmiş; `3×230/400 V` ifadesi açık kuralı tetikleyerek faz
tipi `trifaz`, faz güven skoru 100 olarak çıkarılmıştır. OCR ayrıca
`0.25–5(100) A`, sayaç tipi ve standart bilgilerini okuyabilmiştir. Bu sonuç tek
örnek üzerindeki işlevsel testtir; genel sayaç saha doğruluğu olarak
yorumlanmamalıdır.

### 8.2. Gerçek fatura testi

Kullanıcı tarafından çekilmiş 6912 × 9216 piksel Enerjisa faturasında YOLO güveni
0,27 kalmış ve güvenilir kutu üretememiştir. Tam görüntü parçalı OCR geri dönüşü
faturayı yedi anahtar kelime kanıtıyla doğrulamış ve yaklaşık 193 metin bölgesi
üretmiştir. Alan çıkarma sonuçları aşağıdadır:

**Tablo 6. Gerçek Enerjisa faturasında çıkarılan alanlar**

| Alan | Çıkarılan sonuç | Kanıt/yöntem |
|---|---:|---|
| Şirket | Enerjisa | Şirket metni eşleşmesi |
| Sözleşme/anlaşma gücü | 3,0 kW | `1,000/-/3,000`, birleşik alan kuralı |
| Çarpan | 1,0 | Birleşik alan kuralı |
| Demand | Bulunmuyor | Birleşik değerde `-` |
| Dönem tüketimi | 246,186 kWh | Tek Zaman endeks fark sütunu |
| Günlük ortalama | 8,206 kWh/gün | Fatura Ort. Tüketim etiketi |
| Ödenecek tutar | 675,00 TL | Etiket-konum-birim eşleşmesi |
| Fatura dönemi | 04/2026 | Satır içi etiket eşleşmesi |
| Tarife | Mesken, tek zamanlı, alçak gerilim | Tüketici grubu sınıflandırması |

Sözleşme gücü alanında ham değer `1,000/-/3,000`, etiket
`Çarpan/Demand/Anl. Gücü` ve uygulama güveni 0,91 olarak kaydedilmiştir. Böylece
nihai değer denetlenebilir kanıtla birlikte sunulmuştur.

### 8.3. Farklı ve düşük kaliteli fatura örnekleri

Bir CK Enerji ve iki farklı düşük kaliteli/kırpılmış veri seti görseli ayrıca
denenmiştir. Fatura varlığı doğrulanmış, bir örnekte CK Enerji şirketi
tanınmıştır; ancak kritik alanlar için yeterli görsel kanıt bulunmamıştır. Sistem
sözleşme gücü, dönem tüketimi ve tarife değerlerini uydurmak yerine manuel giriş
istemiştir. Bu sonuç otomatik alan çıkarma başarısı değil, güvenli hata davranışı
olarak değerlendirilmiştir.

### 8.4. Regresyon testleri

Aşağıdaki beş senaryo için otomatik test hazırlanmış ve tümü başarıyla
tamamlanmıştır:

1. `Çarpan/Demand/Anl. Gücü` birleşik satırından 3,0 kW çıkarılması,
2. Ayrı yazılmış `Sözleşme Gücü: 5,00 kW` yapısının çözülmesi,
3. `Sonraki Okuma Dönemi` ifadesinin fatura dönemi sanılmaması,
4. Okuma günü `30` ile endeks farkı `246,186` değerinin karıştırılmaması,
5. Fatura ortalamasının yıllık ortalamaya tercih edilmesi ve tarih adayının
   reddedilmesi.

Bu testler yazılım kurallarını doğrulamaktadır; 70 özgün fatura üzerindeki genel
istatistiksel başarının yerine geçmez.

## 9. Tartışma

Fatura YOLO modelinin iç doğrulama mAP@0.50 değerinin 0,9834 olmasına karşın
gerçek telefon fotoğrafında 0,27 güven üretmesi önemli bir bulgudur. Veri seti
incelendiğinde fatura etiketlerinin neredeyse tamamının görüntünün yaklaşık
%90'ından fazlasını kapladığı görülmüştür. Kaynak görüntülerin çoğunun zaten
kırpılmış faturalardan oluşması nedeniyle model, arka plan içinde faturanın
sınırını öğrenememiştir. Bu durum, dağılım içi doğrulama metriği ile gerçek saha
genellemesinin aynı kavram olmadığını göstermektedir.

Fatura modelini aynı veriyle yeniden eğitmek, bilgi anlamlandırma problemini
çözmeyecektir. Her alanı ayrı nesne olarak işaretlemek de şirket ve şablon başına
çok daha fazla ayrıntılı veri gerektirir. Yalnızca düzenli ifade kullanımı metin
ile etiketin ilişkisini göz ardı ederken, haricî bir büyük dil/görüntü modeline
tam bağımlılık gizlilik, maliyet, tekrarlanabilirlik ve internet bağımlılığı
oluşturabilir. Bu nedenlerle koordinatlı OCR, bulanık metin eşleştirme, şirket ve
genel şablon kuralları, birim doğrulaması ve manuel geri dönüşün birlikte
kullanılması proje koşullarında en dengeli çözüm olarak değerlendirilmiştir.

Hibrit yöntemin temel üstünlüğü açıklanabilirliğidir. Örneğin sistem yalnızca
`3,0 kW` sonucu vermemekte; bu değerin hangi etiketten, hangi ham OCR dizisinden,
hangi konumdan ve hangi kuralla üretildiğini de kaydetmektedir. Bu özellik,
elektrik altyapısı gibi hatalı yorumun güvenlik ve maliyet etkisi oluşturabileceği
bir alanda önemlidir.

## 10. Sınırlılıklar ve Gelecek Çalışmalar

1. Yaklaşık 70 özgün fatura, Türkiye'deki bütün şirket ve tarihsel şablonları
   temsil etmek için yeterli değildir.
2. Roboflow artırılmış türevleri bağımsız gerçek saha örneği olarak
   değerlendirilmemelidir.
3. Alan çıkarma başarısı için henüz bütün özgün faturaları kapsayan manuel gerçek
   değer tablosu oluşturulmamıştır. Bu nedenle genel alan doğruluğu yüzdesi
   raporlanmamıştır.
4. OCR; düşük çözünürlük, bulanıklık, yansıma, kıvrım, ağır perspektif ve kırpma
   koşullarından etkilenmektedir.
5. Tam görüntü parçalı OCR gerçek büyük faturada yaklaşık birkaç dakika
   sürmektedir. Belge kenarı/perspektif düzeltme ve daha küçük güvenli OCR alanı
   performansı iyileştirebilir.
6. Yeni şirket veya şablonlar etiket sözlüğü ve şablon kurallarının genişletilmesini
   gerektirebilir.
7. Sayaç gerilimi ve akım kapasitesi OCR'da okunmakla birlikte bütün yazım
   biçimlerini kapsayan yapılandırılmış ayrıştırıcı henüz tamamlanmamıştır.
8. Sözleşme gücü, sayaç değeri ve tüketim tek başına elektrik tesisatının kurulum
   uygunluğunu kanıtlamaz.

Gelecek deneysel değerlendirmede yaklaşık 70 özgün faturanın şirket ve şablon
kimliğine göre geliştirme/test gruplarına ayrılması önerilmektedir. Her belge için
sözleşme gücü, dönem tüketimi, günlük ortalama ve tarife alanları manuel olarak
etiketlenerek şu ölçütler hesaplanmalıdır:

- alan kapsama oranı,
- doğru alan çıkarma oranı (exact match),
- sayısal alanlarda mutlak hata,
- yanlış pozitif oranı,
- manuel incelemeye yönlendirme oranı,
- şirket ve şablon bazında başarı,
- ortalama işlem süresi.

Gerçek kullanıcı görselleri açık rıza ve anonimleştirmeyle biriktikçe gerçek
sahne fatura tespit modeli yeniden değerlendirilebilir. Yeterli koordinatlı alan
etiketi oluştuğunda belge-anlama modeli ikinci bir yöntem olarak denenebilir;
ancak mevcut veri koşullarında bu çalışma için zorunlu değildir.

## 11. Sonuç

Bu çalışmada elektrik sayacı ve fatura görsellerini elektrikli araç şarj
istasyonu karar desteğinde kullanılabilecek standart verilere dönüştürmek için
çok aşamalı ve açıklanabilir bir yöntem geliştirilmiştir. YOLO11n modelleri belge
ve sayaç bölgesini tespit etmek, PaddleOCR metin ve koordinatları çıkarmak,
RapidFuzz OCR kaynaklı etiket farklılıklarını tolere etmek, düzenli ifadeler ve
konum kuralları ise sayısal değerleri doğru bağlama atamak için kullanılmıştır.

Deneyler, yüksek doğrulama metriğinin gerçek kullanıcı fotoğrafındaki başarıyı
tek başına garanti etmediğini göstermiştir. Bu nedenle düşük güvenli YOLO
tespitini reddeden tam görüntü OCR geri dönüşü, kanıta dayalı alan çıkarma ve
manuel giriş politikası sisteme dâhil edilmiştir. Gerçek test faturasında 3,0 kW
sözleşme gücü ve 246,186 kWh dönem tüketimi doğru bağlamlarıyla çıkarılmış;
yetersiz görsellerde ise sistem değer uydurmak yerine kullanıcı girdisine
yönelmiştir.

Sonuç olarak önerilen hibrit mimari, sınırlı veri koşullarında yalnızca daha fazla
model eğitmeye dayanan yaklaşıma göre daha açıklanabilir, denetlenebilir ve proje
kapsamında uygulanabilir bir çözüm sunmaktadır. Nihai karar destek aşamasında
sayaç ve fatura bulguları birlikte kullanılmalı; eksik alanlar kullanıcıdan
alınmalı ve şarj istasyonu önerisinin elektrikçi incelemesinin yerine geçmediği
açıkça belirtilmelidir.

## Kaynakça

1. Paszke, A. ve ark. (2019). *PyTorch: An Imperative Style, High-Performance
   Deep Learning Library*. Advances in Neural Information Processing Systems 32.
   [NeurIPS kaydı](https://proceedings.neurips.cc/paper/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html)
2. Du, Y. ve ark. (2020). *PP-OCR: A Practical Ultra Lightweight OCR System*.
   arXiv:2009.09941. [Makale](https://arxiv.org/abs/2009.09941)
3. Cui, C. ve ark. (2025). *PaddleOCR 3.0 Technical Report*.
   arXiv:2507.05595. [Teknik rapor](https://arxiv.org/abs/2507.05595)
4. Ultralytics (2024). *Ultralytics YOLO11 Documentation*.
   [Resmî dokümantasyon](https://docs.ultralytics.com/models/yolo11/)
5. RapidFuzz Project. *RapidFuzz fuzz.partial_ratio Documentation*.
   [Resmî dokümantasyon](https://rapidfuzz.github.io/RapidFuzz/Usage/fuzz.html)
