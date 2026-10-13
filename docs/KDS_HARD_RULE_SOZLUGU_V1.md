# KDS Hard Rule Sözlüğü V1

**Tarih:** 2026-09-27  
**Kural sayısı:** 8

Hard rule katmanı ürün puanı üretmez. Teknik olarak açıkça uyumsuz, veri bakımından değerlendirilemez veya haricî doğrulama isteyen alternatifleri sınıflandırır. Kullanılabilecek durumlar `DEGERLENDIR`, `ELE`, `VERI_YETERSIZ` ve `DOGRULAMA_GEREKLI` değerleridir.

## Sonuç semantiği ve öncelik

1. `HR01` başarısızsa kayıt terminal olarak `VERI_YETERSIZ` olur ve hesaplamaya sokulmaz.
2. HR01'i geçen kayıtta açık, bağımsız bir uyumsuzluk varsa `ELE` sonucu; fiyat, garanti veya akıllı özellikle telafi edilmeden uygulanır.
3. Açık eleme yoksa, manuel/haricî kanıt gereken herhangi bir kural `DOGRULAMA_GEREKLI` üretir.
4. Bütün uygulanabilir kurallar geçerse `DEGERLENDIR` elde edilir.

`VERI_YETERSIZ` ürünün kötü olduğu anlamına gelmez. `DOGRULAMA_GEREKLI`, ev fazı veya ürün özel davranışı gibi doğrulanabilir belirsizlikler içindir.

| rule_id | rule_name | girdi_alanlari | kosul | sonuc | eksik_veri_davranisi | gerekce | ilgili_test_senaryolari |
|---|---|---|---|---|---|---|---|
| HR01 | KDS veri kullanılabilirliği kapısı | charger.kds_veri_kullanilabilir; charger.kds_eksik_alanlar; charger.kds_veri_uyarilari | Normal değerlendirmede charger.kds_veri_kullanilabilir = Hayır | VERI_YETERSIZ | Alternatif otomatik sıralama matrisine alınmaz; eksik alanlar aynen raporlanır. Değer tahmin edilmez. | Bayrak ürün kalitesini değil, asgari teknik kanıtın hesaplamaya yeterliliğini gösterir. Sonuç ürünün kötü veya teknik olarak uyumsuz olduğu anlamına gelmez. | D3-015, D3-016, D3-017; POOL_EKSIK_VERI_3 |
| HR02 | AC konektör uyumu | vehicle.ac_konnektor_tipi; charger.ac_konnektor_tipi | İki konektör açıkça farklıysa ELE; eşitse sonraki kontrole geç | ELE / DEGERLENDIR | Taraflardan biri null/Bilinmiyor ise DOGRULAMA_GEREKLI; eşitlik varsayılmaz. | Fiziksel bağlantı uyumsuzluğu soft özelliklerle telafi edilemez. Mevcut katalog Type 2 ağırlıklıdır; kural gelecekteki farklı tipler için yine korunur. | Mevcut D1–D4'te negatif konektör örneği yok; yeni negatif test vakası eklenmelidir. |
| HR03 | Monofaz konut–wallbox besleme uyumu | home.faz; charger.tek_faz_destegi; charger.tek_faz_azami_guc_kw; charger.tek_faz_azami_akim_a | home.faz = monofaz ve charger.tek_faz_destegi = Hayır ise ELE; Evet ise tek faz yolu değerlendir | ELE / DEGERLENDIR | tek_faz_destegi = Bilinmiyor veya gerekli tek faz güç/akımı yoksa DOGRULAMA_GEREKLI ya da HR01 kapsamındaysa VERI_YETERSIZ. | Wallboxın şebekeden tek faz beslenebilmesi, aracın faz kabulünden ayrı bir ön koşuldur. | D4-001…D4-007; özellikle D4-004, D4-005, D4-006 |
| HR04 | Trifaz konut değerlendirme yolu | home.faz; charger.uc_faz_destegi; charger.tek_faz_destegi; faza özel wallbox güç/akım alanları | home.faz = trifaz ve uc_faz_destegi = Evet ise üç faz yolu değerlendirilir. Yalnız tek faz çalışan wallbox otomatik ELE yapılmaz. | DEGERLENDIR / DOGRULAMA_GEREKLI | Üç faz yolu Bilinmiyor ise veya trifaz evde yalnız tek faz kurulumun faz dengesi/saha koşulları yoksa DOGRULAMA_GEREKLI. | Trifaz besleme tek faz wallboxı fiziksel olarak imkânsız kılmaz; ancak hangi faza, hangi korumayla bağlanacağı mevcut veriyle doğrulanamaz. | D4-008…D4-012, D4-017…D4-019 |
| HR05 | Ev faz bilgisinin belirsizliği | home.faz | home.faz = belirsiz | DOGRULAMA_GEREKLI | Faza bağlı etkin güç ve kesin teknik sıralama üretilmez; kullanıcı/sayaç/elektrikçi doğrulaması istenir. | Sistem genelinde DOGRULAMA_GEREKLI, dış bilgiyle çözülebilecek belirsizlikler için kullanılır. VERI_YETERSIZ ise katalog kaydının asgari hesaplama kanıtı olmadığı durumlara ayrılmıştır. | D3-001, D3-004, D3-006, D3-008, D3-010, D3-019 |
| HR06 | Kurulum yeri uygunluğu | user.kurulum_yeri; charger.ic_mekan_uygun; charger.dis_mekan_uygun | Seçilen yer için ilgili uygunluk alanı = Hayır ise ELE; Evet ise devam | ELE / DEGERLENDIR | İlgili uygunluk alanı Bilinmiyor/null ise DOGRULAMA_GEREKLI. IP sınıfından sessizce Evet türetilmez. | Açık çevresel uygunsuzluk fiyat veya akıllı özelliklerle telafi edilemez; Bilinmiyor ise ürün hakkında olumsuz sonuç uydurulmaz. | D4-020; D3-020; iç/dış mekân pozitif örnekleri D4-003, D4-009, D4-020 kaynak vakaları |
| HR07 | Çapraz faz araç davranışı | home.faz; charger.uc_faz_destegi; charger.uc_faz_faz_basina_akim_a; vehicle.ac_tek_faz_destegi; vehicle.ac_uc_faz_destegi; vehicle.ac_tek_faz_azami_akim_a; charger.nominal_gerilim; ürün özel kanıtı | Üç faz çalışan wallbox + yalnız tek faz kabul eden araç otomatik ELE değildir. Ürün özel davranış kanıtı varsa ilgili yol değerlendirilir. | DEGERLENDIR / DOGRULAMA_GEREKLI | Ürün davranışı veya kaynaklandırılmış faz–nötr gerilim kanıtı yoksa etkin güç null ve DOGRULAMA_GEREKLI. | Wallbox besleme fazı ile araç onboard charger faz kabulü aynı kavram değildir; go-e kanıtı başka markalara genellenmez. | D4-013…D4-016 |
| HR08 | Sözleşme gücünün kullanım sınırı | home.sozlesme_gucu_kw; home.donem_tuketimi_kwh; home.gunluk_ortalama_kwh | Bu alanlar hiçbir alternatif için güvenli güç, ana sigorta sınırı veya otomatik eleme eşiği olarak kullanılmaz. | DEGERLENDIR | Eksikliği teknik wallbox gücüyle doldurulmaz. Alanlar yalnız bağlam/uyarı olarak taşınır. | Sözleşmesel kapasite ve geçmiş enerji tüketimi pano, hat, koruma ve eşzamanlı yük kapasitesini kanıtlamaz. | Kaynak teknik vaka TC-22; bütün D1–D4 senaryoları için sistem guardrail'i |

## Hard rule olmayan fakat koşullu teknik alanlar

RCD/RDC-DD, dahili/harici koruma ve benzeri alanlar “varsa daha iyi” biçiminde benefit kriterine çevrilmez. Bunlar ürünün kurulum mimarisini ve elektrikçinin sağlaması gereken koşulları açıklar. Eksik koruma verisi otomatik ürün bonusu veya cezası değildir.
