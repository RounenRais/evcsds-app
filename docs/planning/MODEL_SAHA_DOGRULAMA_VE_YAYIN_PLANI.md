# Sayaç ve Fatura Modelleri: Saha Doğrulama ve Yayın Planı

**Durum (2026-10-11):** Kontrollü uçtan uca örnekler çalışıyor. Otomatik `home` değerleri kullanıcı onayı bekleyen adaylar olarak işaretleniyor; bağımsız saha doğruluğu ve herkese açık servis kapasitesi henüz ölçülmedi.

## Bugün doğrulananlar

| Kontrol | Gözlem | Yorum |
|---|---|---|
| Sayaç: `sayac_photos/sayac001.jpg` | Sayaç bulundu; faz `trifaz`; 26 OCR bölgesi; analiz ~40 saniye | Tek örnek işlev testi, saha doğruluğu ölçümü değil |
| Fatura: `electric_bills_test_image.jpg` | Tam görsel OCR ile fatura doğrulandı; sözleşme gücü 3,0 kW; dönem tüketimi 246,186 kWh; tarife mesken/tek zamanlı/AG; 193 OCR bölgesi; analiz ~390 saniye | Geliştirmede kullanılan örnek; bağımsız test değil. Süre doğrudan CLI üzerinde ham 6912×9216 görsele aittir; API yeniden boyutlandırmasıyla süre ayrıca ölçülmelidir. |
| Alan çıkarma regresyonu | 5/5 test geçti | Sentetik OCR satırı testidir, yeni fotoğraflardaki OCR doğruluğunu ölçmez |
| KDS ev girdi eşlemesi | Güncel regresyon kümesinde 4/4 test geçti | Teknik olarak gerekli eksik alanlar manuel doğrulamaya ayrılıyor; dolu alanlar kullanıcı onayı bekliyor ve ham OCR metni birleşik yanıta taşınmıyor |
| HTTP `POST /analyze/home` (örnek fotoğraflarla) | `200 OK`; toplam ~172 saniye; faz `trifaz`, güç 3,0 kW, tarife doğru; dönem tüketimi `null` ve manuel doğrulama istendi | API'nin 6000 piksel uzun kenar sınırındaki küçültmesi bu örnekte tüketim alanını kaybettirdi. 6912×9216 CLI sonucu API sonucu yerine geçirilmemelidir. |

Sayaç faz `guvenskor=100` ve fatura alan `guven` değerleri **kalibre edilmiş doğruluk olasılıkları değildir**. Yüzde başarı olarak sunulmamalıdır.

Bu örnekte parlak belge alanına göre otomatik kırpma denemesi fatura alt bölümünü kestiği için etkinleştirilmedi. Farklı telefon fotoğraflarında doğrulanmış belge sınırı yöntemi olmadan bu kestirme kullanılmamalıdır.

Güncel yayın değerlendirme şablonu `planning/FATURA_SAHA_DOGRULAMA_SABLONU.csv` içinde sekiz pilot fatura ve veri setinden dört fatura olmayan geliştirme görseli listeler. Kullanıcının görsel okumasıyla **6 sözleşme gücü ve 4 tarife etiketi** girildi; bunlar henüz ikinci kişiyle karşılaştırılmadı. **Kaynağı bağımsızlığı doğrulanmış örnek sayısı 0'dır.** Yıl bazlı günlük tüketim değerleri ayrı notlarda tutuldu; fatura dönemi toplam tüketimine dönüştürülmedi. `syctest7` üzerindeki `3000` ifadesinin birimi/biçimi netleşene kadar güç etiketi boş tutuldu. `python bill_release_eval.py --validate-only` etiket durumunu model çalıştırmadan kontrol eder; değerlendirme aracı API ön işlemesiyle alan ve gecikme sayımlarını yapar. Görseller ve ham OCR rapora kaydedilmez.

Son API ön işlemli regresyon kontrolünde `syctest4.jpg` için fatura doğrulandı ve sözleşme gücü 6,408 kW olarak çıkarıldı; `home` yanıtı `kullanici_onayi_gerekli`, `kdsye_dogrudan_aktarilabilir=false` döndü. Dört mevcut fatura olmayan geliştirme görselinin tamamında `fatura_bulundu=false` sonucu alındı. Bu sonuçlar bağımsız saha testi değildir; özellikle daha çeşitli ve yeni negatif görseller gerekir.

Kullanıcı etiketleriyle altı faturanın **düzeltme öncesi** API ön işlemli taramasında güç alanı 4 kez doğru bulundu, 2 kez kaçırıldı; etiketli dört tarifeden yalnız biri doğru sınıflandırıldı, biri uyuşmayan dolu sonuç verdi ve ikisi kaçırıldı. Hedefli OCR ve etiket-değer eşleştirme düzeltmeleri sonrasında **aynı son kod sürümüyle** altı fatura tekrar koşuldu: altısında fatura tespiti ve kullanıcı etiketine göre güç doğru; etiketli dört tarifeden üçü doğru, biri boş kaldı. Dönem toplamları bu altı görselde boş kaldı ve doğrulanmış dönem toplamı etiketi olmadığı için doğruluk hesaplanmadı. Ayrıntılı örnek tablosu `MODEL_TESTIMAGELAST_PILOT_DEGERLENDIRME.md` içindedir. Etiketlerin ikinci okuyucuyla ve örneklerin bağımsızlıkla doğrulanmamış olması nedeniyle bunlar yalnız geliştirme teşhisidir.

## Bağımsız test kümesi

1. Eğitim, kural geliştirme ve demo için kullanılan görsellerden **ayrı** gerçek telefon fotoğrafları toplayın. Aynı belge/sayacın farklı kırpma veya ışık türevlerini farklı kümelere bölmeyin.
2. İlk pilotta farklı marka ve çekim koşullarından en az 50 sayaç, farklı şirket/şablon ve çekim koşullarından en az 50 fatura, ayrıca en az 10 fatura olmayan negatif görsel hedefleyin. Bu sayılar geniş ölçekli doğruluk garantisi vermez; hata türlerini görmeye yarayan ilk saha ölçümüdür.
3. Her fotoğraf için yalnız ilgili gerçek değerleri ayrı tabloda iki kişiyle doğrulayın: sayaçta faz; faturada sözleşme gücü, dönem tüketimi, tarife ve varsa dönem. Belge üzerindeki alan gerçekten yoksa bunu `belgede_yok` olarak ayırın. Ad, adres, TCKN ve müşteri numarası etiket tablosuna girmesin.
4. Görselleri sağlayıcı/şablon, çözünürlük, odak, yansıma, kırpma ve çekim açısına göre gruplayın. Aynı sürüm ve donanımla çalıştırıp süreleri kaydedin.

## Ölçülecek sonuçlar

| Katman | Ölçüm |
|---|---|
| Sayaç tespiti | Bulundu/bulunmadı; yanlış nesne tespiti; fotoğraf koşuluna göre dağılım |
| Faz | `monofaz`/`trifaz` doğru sayısı; yanlış kesin karar; `belirsiz` oranı |
| Fatura tespiti | Doğru belge onayı; negatif görselde yanlış onay; YOLO ve tam OCR kullanım oranı |
| Kritik alanlar | Sözleşme gücü ve tüketimde birimle birlikte doğru eşleşme; tarife doğru sınıf; `belgede_yok`, `null`, yanlış dolu ve manuel oranları ayrı |
| Kullanılabilirlik | Uçtan uca başarı, hata/timeout, API yolu için p50/p95 süre ve eşzamanlı istek kuyruğu |
| Veri gizliliği | Yeni `/analyze/home` yanıtında ham OCR, ad, adres veya abonelik numarası bulunmaması |

Özellikle **yanlış fakat dolu kritik alan** sayısını ayrı raporlayın. `manuel_dogrulama_gerekli` güvenli geri çekilmedir; otomatik başarı sayılmamalıdır. Farklı şirketler ve telefon çekimi koşulları için ayrı oranlar verin. Küçük örneklemlerde sonuçları belirsizlik aralığıyla yorumlayın.

## Yayın kapıları ve sorumluluk

1. **Model ekibi:** Bağımsız test kümesi, gerçek değer tablosu, alan bazında hata analizi ve API performans ölçümünü tamamlar. Fatura tam OCR gecikmesini iyileştirip aynı test kümesinde doğrular.
2. **KDS ekibi:** `/analyze/home` içindeki `home` alanlarını V1.1 girdi sözleşmesine bağlar. `manuel_dogrulama_alanlari` eksikleri ister; `onay_bekleyen_alanlar` değerlerini kullanıcı doğrulamasından sonra aktarır. `kdsye_dogrudan_aktarilabilir=false` bayrağı atlanmaz. Sözleşme gücünü güvenli tesisat gücü saymaz.
3. **Web/sunucu ekibi:** API anahtarını tarayıcıya koymadan sunucu üzerinden çağırır; HTTPS, kimlik doğrulama, istek kotası, kuyruk/zaman aşımı ve geçici görsel saklama politikasını uygular. Eski ayrıntılı OCR uçlarını genel kullanıcıya doğrudan açmaz.
4. **Elektrik uzmanı:** Kurulum kararı için ana sigorta, hat, pano, koruma ve topraklama doğrulama akışını onaylar.

Kamuya açılacak başarı ve gecikme eşikleri testten **önce** proje ekibiyle belirlenir. Bağımsız test sonuçları ve bu eşikler olmadan “her fotoğrafta doğru” veya “kuruluma uygun” iddiası kullanılmaz. İlk yayın kontrollü beta olarak yapılır; hata kayıtları kişisel veri içermeyecek biçimde izlenir.
