# KDS V1.1 Teknik Eşleşme Kuralları Taslağı

**Tarih:** 2026-09-27  
**Durum:** Semantik taslak; karar algoritması veya kurulum onayı değildir.

## 1. Amaç

Bu belge `home`, `vehicle` ve `charger` alanlarının hangi teknik ilişkiyi anlattığını ayırır. Amaç, wallboxın besleme fazı ile aracın onboard charger faz kabulünün aynı kavram sanılmasını ve sözleşme gücünden güvenli tesisat kapasitesi türetilmesini önlemektir.

## 2. İki farklı faz kavramı

| Kavram | Ne anlatır? | Alanlar | Ne anlatmaz? |
|---|---|---|---|
| Araç faz desteği | Aracın onboard AC charger'ının tek veya üç faz üzerinden enerji kabulü ve ilgili üst sınırı | `vehicle.ac_tek_faz_*`, `vehicle.ac_uc_faz_*` | Evin fazı veya wallboxın nasıl beslendiği |
| Wallbox besleme/çalışma faz desteği | Wallbox varyantının tesisattan tek veya üç faz beslenerek çalışması ve ilgili üst sınırı | `charger.tek_faz_*`, `charger.uc_faz_*`, `charger.nominal_gerilim` | Aracın kaç faz kabul ettiği |

`charger.tek_faz_destegi=Hayır`, yalnız wallboxın tek faz şebeke beslemesinin açıkça desteklenmediğini bildirir. Üç faz beslenen aynı wallboxın tek faz onboard charger taşıyan araçla çalışıp çalışmadığı bundan tek başına çıkarılamaz.

## 3. Teknik durum sözlüğü

- `uygun`: Mevcut alanlar ve ürün kanıtı ilgili ilişki için yeterlidir. Kurulum güvenliği onayı değildir.
- `uygun_degil`: Açık kaynaklı alanlar ilgili ilişkiyi dışlar.
- `dogrulama_gerekli`: `Bilinmiyor`, ürün özel davranışı veya saha bilgisi olmadan kesinleştirilemez.

## 4. A — Ev → Wallbox

Bu ilişki wallboxın konut beslemesinde çalıştırılabilirliğini ele alır:

- Monofaz evde `charger.tek_faz_destegi=Evet` olmalıdır. `Hayır` ise ilişki `uygun_degil`; `Bilinmiyor` ise `dogrulama_gerekli` olur.
- Trifaz evde `charger.uc_faz_destegi=Evet` ise üç faz çalışma yolu veri bakımından açıktır.
- Trifaz ev, tek faz wallboxı otomatik uygunsuz yapmaz. Bir faz üzerinden kurulum mümkün olabilir; ancak faz dengesi, yerel sınırlar, pano/koruma ve hat düzeni veri paketinde olmadığı için `dogrulama_gerekli` kullanılır.
- `home.sozlesme_gucu_kw` yalnız sözleşmesel/bağlantısal kapasite bağlamıdır. Ev → Wallbox sonucunu tek başına `uygun` yapmaz.

## 5. B — Wallbox → Araç

Bu ilişki wallbox ile araç arasındaki bağlantı ve onboard charger sınırını ele alır:

1. `charger.ac_konnektor_tipi` ile `vehicle.ac_konnektor_tipi` ayrı kontrol edilir. Pilot ve araç çekirdeğinde Type 2 eşleşir; farklı tip gelecekte otomatik varsayılmaz.
2. Araç yalnız tek faz kabul ediyorsa üç faz wallbox otomatik fiziksel uyumsuz sayılmaz.
3. Aynı faz yolunda araç ve wallbox gücü varsa teorik üst sınır iki değerin küçüğüdür.
4. Üç faz beslenen wallbox + tek faz araç çapraz durumunda ürünün tek fazlı araç davranışı ve faz–nötr gerilimi ayrıca kanıtlanır.

go-e resmi SSS'si, yalnız tek faz kabul eden aracın go-e Charger ile tek faz şarj olacağını; üreticinin faz tablosu ise 11 kW go-e cihazda tek faz araç için 1,4–3,7 kW aralığını açıklar. Bu nedenle seçili `GOE_CHARGER_GEMINI_11_TR` için ürün özelinde kanıt vardır. Bu kanıt Tesla, Vestel, Easee veya başka markaya genellenmez.

## 6. Etkin güç durumları

| Durum | Ön koşul | Teorik araç–wallbox üst sınırı | Durum |
|---|---|---|---|
| A | Monofaz ev; wallbox tek faz `Evet`; araç tek faz `Evet`; Type 2 eşleşir | `min(vehicle.ac_tek_faz_azami_guc_kw, charger.tek_faz_azami_guc_kw)` | Alanlar doluysa `uygun` |
| B | Trifaz ev; wallbox üç faz `Evet`; araç üç faz `Evet`; Type 2 eşleşir | `min(vehicle.ac_uc_faz_azami_guc_kw, charger.uc_faz_azami_guc_kw)` | Alanlar doluysa `uygun` |
| C | Trifaz ev; wallbox üç faz besleniyor; araç yalnız tek faz kabul ediyor | Kavramsal `I_etkin=min(vehicle.ac_tek_faz_azami_akim_a, charger.uc_faz_faz_basina_akim_a)`; güç için gerilim ve ürün davranışı gerekir | Ürün kanıtı yoksa `dogrulama_gerekli` |
| D | Monofaz ev; wallbox tek faz desteği `Hayır` | Hesaplanmaz | `uygun_degil` |

Bu üst sınırlar konutun güvenli kullanılabilir gücünü içermez. Pano, ana sigorta, hat, koruma ve eşzamanlı yük ayrıca doğrulanır.

## 7. Nominal gerilim kararı

Pilot katalogda `nominal_gerilim` 10/10 üründe üretici kaynağıyla doludur ve Durum C'de akımdan güce geçişin kanıt bağlamını taşır. Bu nedenle alan V1.1 çekirdeğine **ham metin olarak** eklenmiştir.

Örnek biçimler `230 V tek faz / 400 V üç faz`, `380-415 V üç faz` ve `200-240 V AC tek faz` şeklindedir. Sistem bu metinlerden sessizce sayısal değer çıkarmamalıdır. İleride kaynak açıkça destekliyorsa `tek_faz_nominal_gerilim_v` ve `uc_faz_fazlar_arasi_gerilim_v` alanları ayrı önerilebilir; bu taslakta üretilmemiştir.

## 8. DLM semantiği

DLM; ev yükünü bir sayaç/enerji yönetimi bileşeniyle izleyerek wallbox akım sınırını değiştirebilen kurulum özelliğidir. Wi-Fi, Bluetooth veya mobil uygulama varlığı DLM kanıtı değildir.

- DLM `Evet` olsa bile "bu evde 22 kW uygundur" sonucu çıkarılmaz.
- Ölçüm noktası, ana/hat sınırı ve üreticiye göre harici sayaç/modül gerekir.
- Tesla, dinamik güç yönetiminde canlı pano ölçümü için enerji sayacı kullanılmasını; go-e ise Controller ile yük dengelemesini açıklar.
- Sözleşme gücü bağlam sağlayabilir, fakat güvenli tesisat kapasitesi yerine konmaz.

## 9. Ürün kanıtı ve sınırlar

| Kanıt | Desteklediği sonuç | Sınırı |
|---|---|---|
| [go-e resmi SSS](https://go-e.com/en/support/faqs) | go-e Charger tek/üç faz çalışır; tek faz araç tek faz şarj olur; Type 2 araç bağlantısı desteklenir | Yalnız go-e ürün ailesine doğrudan uygulanır |
| [go-e faz tablosu](https://go-e.com/en/magazine/single-phase-three-phase-ev-charging) | 11 kW go-e + tek faz araç için 1,4–3,7 kW; araç/wallbox zincirinde zayıf halka sınırı | Ülke sınırlamaları ve kurulum kapasitesi ayrıca geçerlidir |
| [Tesla güç besleme seçenekleri](https://energylibrary.tesla.com/docs/Public/Charging/WallConnector/Gen3/Install/3PT2/EMEA/en-us/GUID-84A0811C-F362-4026-BF76-0C737A489F4B.html) | Gen 3 cihazın tek/üç faz besleme seçenekleri ve 230 V L-N gereksinimi | Özel 230 V delta yapılandırmasında araç erişimi sınırlaması vardır; genelleme yapılamaz |
| [Tesla Wall Connector kılavuzu](https://www.tesla.com/sites/default/files/support/charging/Gen_3_Wall_Connector_Manual_UK.pdf) | Gerçek hızın wallbox çıkışı ve onboard charger tarafından sınırlandığı | Tek faz araç + üç faz besleme davranışını bütün markalar için kesinleştirmez |
| [Tesla Türkiye güç yönetimi](https://www.tesla.com/tr_tr/support/charging/wall-connector/power-management) | Dinamik yönetim için ölçüm ve onaylı güç ölçer bağlamı | DLM, tesisat uygunluk onayı değildir |

## 10. Uygulama sınırı

Bu belge test vakalarının beklenen semantiğini tanımlar. Çalışan API, eşleştirme motoru, puanlama veya ürün önerisi geliştirilmemiştir.
