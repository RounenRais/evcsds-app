# KDS Türetilmiş Değişkenler Sözlüğü V1.1

**Sürüm tarihi:** 2026-09-27

Bu belge karar algoritması değildir. Teknik kavramların hangi kanıt koşullarında hesaplanabileceğini tanımlar; ürün puanı, sıralaması veya kurulum onayı üretmez.

## `gunluk_arac_enerji_ihtiyaci_kwh`

```text
gunluk_arac_enerji_ihtiyaci_kwh
  = user.gunluk_ortalama_km × vehicle.wltp_tuketim_kwh_100km / 100
```

WLTP tüketimi eksikse değer `null` kalır; batarya kapasitesi/menzilden otomatik tahmin edilmez. Bu değer araç bataryasına teorik günlük enerji ihtiyacıdır; şebekeden çekilecek enerji değildir.

## `arac_wallbox_etkin_guc_kw`

V1.1'de bu değişken tek bir koşulsuz `min()` işlemi değildir. Önce Ev → Wallbox besleme ilişkisi, Type 2 bağlantı uyumu ve ürünün araç faz davranışı için kanıt yeterliliği belirlenir. Ardından uygun faz bağlamındaki araç ve wallbox sınırları kullanılır.

### Durum A — Monofaz ev, tek faz çalışan wallbox, tek faz kabul eden araç

Gerekli alanlar açık ve uyumluysa teorik araç–wallbox üst sınırı:

```text
min(vehicle.ac_tek_faz_azami_guc_kw,
    charger.tek_faz_azami_guc_kw)
```

Bu sonuç konutun güvenli kullanılabilir gücünü içermez.

### Durum B — Trifaz ev, üç faz çalışan wallbox, üç faz kabul eden araç

Gerekli alanlar açık ve uyumluysa teorik üst sınır:

```text
min(vehicle.ac_uc_faz_azami_guc_kw,
    charger.uc_faz_azami_guc_kw)
```

Bu sonuç da pano, ana sigorta, eşzamanlı yük, kablo veya koruma sınırını içermez.

### Durum C — Trifaz ev, üç faz beslenen wallbox, yalnız tek faz kabul eden araç

Bu durum otomatik `uygun_degil` değildir. Ürün bu kullanım biçimini açıkça destekliyorsa kavramsal akım sınırı:

```text
I_etkin = min(vehicle.ac_tek_faz_azami_akim_a,
              charger.uc_faz_faz_basina_akim_a)
```

Tek faz güç değerlendirmesi için ayrıca kaynaklandırılmış faz–nötr gerilim ve wallboxın tek fazlı araçla çalışma davranışı gerekir. `charger.nominal_gerilim` V1.1'e ham metin olarak eklenmiştir; metinden otomatik `230` veya başka bir sayı türetilmez. Ürün davranışı veya gerilim kanıtı yetersizse `arac_wallbox_etkin_guc_kw=null` ve `dogrulama_gerekli` kullanılır.

go-e, kendi Charger ailesi için tek faz onboard charger taşıyan aracın tek faz şarj olacağını ve 11 kW cihazda tek faz araç gücünün 1,4–3,7 kW aralığında olduğunu açıkça belgelemektedir. Bu kanıt go-e ürününe özgüdür; diğer markalara otomatik aktarılmaz.

### Durum D — Monofaz ev, seçilen wallbox varyantında tek faz besleme desteği `Hayır`

Ev → Wallbox ilişkisi `uygun_degil` olur ve etkin güç hesaplanmaz. Bu sonuç aracın tek/üç faz kabulünden bağımsızdır. Wallboxın yalnız üç faz besleme desteği açıkken monofaz evde doğrudan kullanılabilir varsayılmaz.

### Trifaz evde tek faz wallbox

Trifaz beslemenin bulunması tek faz wallboxı otomatik uygunsuz yapmaz; bir faz üzerinden kurulum teknik olarak mümkün olabilir. Faz dağılımı, dengesizlik sınırları, yerel şartlar ve koruma seçimi mevcut veride bulunmadığından Ev → Wallbox sonucu `dogrulama_gerekli`, etkin güç ise kurulum doğrulanana kadar `null` kalır.

## `gunluk_ihtiyaci_karsilama_suresi_saat`

```text
gunluk_ihtiyaci_karsilama_suresi_saat
  = gunluk_arac_enerji_ihtiyaci_kwh
    / (arac_wallbox_etkin_guc_kw × sarj_verimi_katsayisi)
```

`sarj_verimi_katsayisi` kaynaklandırılmamış sabit bir gerçek olarak atanmaz. Etkin güç `null` veya teknik durum `dogrulama_gerekli` ise süre kesin sonuç olarak üretilmez.

## `teknik_eslesme_durumu`

- `uygun`: Mevcut veri ve ürün kanıtı ilgili teknik ilişkiyi destekler. Kurulum onayı değildir.
- `uygun_degil`: Açık alanlar ilgili teknik ilişkiyi dışlar; örneğin monofaz ev ve tek faz besleme desteği `Hayır` olan wallbox.
- `dogrulama_gerekli`: `Bilinmiyor` alan, çapraz faz davranışı, gerilim yorumu veya saha/elektrikçi bilgisi olmadan kesin sonuç verilemez.

## Sözleşme gücü ve DLM sınırı

`home.sozlesme_gucu_kw` bu formüllerde güvenli wallbox gücü olarak kullanılmaz. DLM, ölçülen ev yüküne ve kurulmuş limite göre şarj akımını değiştirebilir; ancak DLM varlığı, belirli bir gücün güvenli/uygun olduğunu tek başına kanıtlamaz. Harici sayaç/modül ve kurulum ayarı üreticiye göre ayrıca doğrulanır.

## Kaynaklar

- [go-e resmi SSS: tek faz araçla tek faz şarj ve otomatik faz davranışı](https://go-e.com/en/support/faqs)
- [go-e resmi faz açıklaması: 11 kW cihazda tek faz araç için 1,4–3,7 kW](https://go-e.com/en/magazine/single-phase-three-phase-ev-charging)
- [Tesla Gen 3 güç besleme seçenekleri: tek/üç faz ve 230 V L-N koşulu](https://energylibrary.tesla.com/docs/Public/Charging/WallConnector/Gen3/Install/3PT2/EMEA/en-us/GUID-84A0811C-F362-4026-BF76-0C737A489F4B.html)
- [Tesla Türkiye güç yönetimi: dinamik yönetim ve harici güç ölçer bağlamı](https://www.tesla.com/tr_tr/support/charging/wall-connector/power-management)
