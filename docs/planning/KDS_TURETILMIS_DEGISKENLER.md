# KDS Türetilmiş Değişkenler Sözlüğü

Bu belge ileride hesaplanabilecek ara değişkenleri tanımlar; karar algoritması, eşik, ağırlık veya ürün sıralaması içermez.

## 1. `gunluk_arac_enerji_ihtiyaci_kwh`

Kullanıcının tipik günlük mesafesi ile aracın WLTP tüketiminden türetilen teorik araç enerji ihtiyacıdır.

```text
gunluk_arac_enerji_ihtiyaci_kwh
  = gunluk_ortalama_km × wltp_tuketim_kwh_100km / 100
```

- Girdiler: `user.gunluk_ortalama_km`, `vehicle.wltp_tuketim_kwh_100km`.
- Birim: kWh/gün.
- WLTP tüketimi eksikse hesaplanmaz; batarya kapasitesi/menzilden otomatik tahmin edilmez.
- Bu değer şebekeden çekilecek gerçek enerji değildir; şarj kaybı/verim ayrıca tanımlanmalıdır.

## 2. `arac_wallbox_etkin_guc_kw`

Ev tarafındaki kullanılabilir güç hesaba katılmadan önce, konutun doğrulanmış faz bağlamında araç ve wallboxın faza özel AC üst sınırlarının birlikte belirlediği teorik üst güçtür.

```text
arac_wallbox_etkin_guc_kw
  = min(arac_faza_ozel_ac_siniri_kw, wallbox_faza_ozel_ac_siniri_kw)
```

- Birim: kW.
- Konektör ve faz uyumluluğu doğrulanmadan hesaplanmaz.
- Genel araç AC gücü yerine faza özel araç alanları kullanılır.
- Konutun güvenli kullanılabilir şarj gücü henüz tanımlı değildir; bu nedenle sözleşme gücü veya sayaç azami akımı bu değişkene eklenmez.
- Bu değer kurulum onayı veya gerçekleşecek sabit güç garantisi değildir.

## 3. `gunluk_ihtiyaci_karsilama_suresi_saat`

Günlük araç enerji ihtiyacının, teknik olarak elde edilebilen etkin AC güç altında yaklaşık kaç saatte karşılanacağını ifade eder.

```text
gunluk_ihtiyaci_karsilama_suresi_saat
  = gunluk_arac_enerji_ihtiyaci_kwh
    / (arac_wallbox_etkin_guc_kw × sarj_verimi_katsayisi)
```

- Birim: saat.
- `sarj_verimi_katsayisi` V1 kaynak verilerinde yoktur ve sabit bir gerçek olarak atanmayacaktır.
- Katsayı ileride kaynaklandırılmış varsayım, ölçüm veya yapılandırma olarak ayrıca tanımlanmalıdır.
- Güvenli konut güç sınırı tanımlanıncaya kadar sonuç yalnız araç–wallbox teorik üst sınırına dayanır ve gerçek kurulum süresini garanti etmez.
- Sonuç, `user.evde_sarj_icin_uygun_sure_saat` ile ileride karşılaştırılabilir; bu belge karşılaştırma kuralı veya karar üretmez.

## Eksik veri davranışı

Herhangi bir zorunlu girdi `null` veya `Bilinmiyor` ise ilgili türetilmiş değer `null` kalır ve neden kalite/uyarı alanında taşınır. Eksik değer sıfır kabul edilmez.
