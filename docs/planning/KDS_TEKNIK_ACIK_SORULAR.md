# KDS V1.1 Teknik Açık Sorular

**Tarih:** 2026-09-27

Bu rapor teknik semantik ve veri yeterliliğini sınıflandırır; ürün önerisi veya kurulum onayı değildir. Test çalışma kitabında 22 vaka vardır: 14 vaka mevcut veriyle kesin `uygun/uygun_degil`, 8 vaka `dogrulama_gerekli` olarak tanımlanmıştır.

## Kaynakla çözüldü

- **Araç fazı ile wallbox besleme fazı farklı kavramlardır.** Araç alanları onboard charger kabulünü, wallbox alanları tesisattan çalışma/besleme düzenini anlatır.
- **Type 2 uyumu ayrı kontroldür.** Konektör eşleşmesi faz ve güç davranışını tek başına kanıtlamaz.
- **Aynı faz bağlamında teorik üst sınır zayıf halka tarafından belirlenir.** Monofaz A ve trifaz B durumlarında faza özel güçlerin küçüğü kullanılabilir; ev güvenli gücü bu değere dâhil değildir.
- **go-e ürün ailesinde üç faz besleme + tek faz araç davranışı belgelenmiştir.** Üretici, tek faz araçta tek faz şarjı ve 11 kW cihaz için 1,4–3,7 kW aralığını açıklar. Bu kanıt yalnız go-e için kullanılmıştır.
- **Nominal gerilim provenansı vardır.** Pilot 10/10 kayıtta üretici kaynaklı ham `nominal_gerilim` bulunduğundan V1.1 çekirdeğine metin olarak taşınmıştır; sayısal gerilim türetilmemiştir.
- **DLM kullanıcı bağlantı özelliği değildir.** Üretici kaynakları DLM'yi ev/pano yükünü ölçüp şarj akımını yöneten kurulum/enerji yönetimi özelliği olarak açıklar.

## Elektrik mühendisi/uzman doğrulaması gerekli

- **Üç faz evde tek faz wallbox kurulumu:** Bir faz üzerinden teknik kurulum mümkün olabilir; faz dengesizliği sınırı, yerel dağıtım kuralları, ana/hat koruması ve pano bağlantısı saha özelidir. Otomatik uygunsuz sayılmamalı, ancak doğrudan uygun da denmemelidir.
- **DLM ile sözleşme gücü ilişkisi:** Sözleşme gücü bağlantısal bağlam sağlayabilir; DLM sınırı, ölçüm noktası, ana koruma ve eşzamanlı yük bilinmeden güvenli wallbox gücü belirlenemez.
- **Güvenli ev kullanılabilir gücü:** Ana sigorta, hat sigortası, kablo kesiti/uzunluğu, pano kapasitesi, RCD/RDC-DD düzeni, topraklama ve eşzamanlı yükün nasıl doğrulanacağı tanımlanmalıdır. Sayaç azami akımı ana sigorta yerine kullanılamaz.
- **Akımdan güç türetme:** Ham `nominal_gerilim` metninin hangi ölçüm/topoloji bağlamında kullanılacağı uzman onayı olmadan otomatik parser kuralına dönüştürülmemelidir.

## Ürün özelinde doğrulama gerekli

- **Üç faz wallbox + yalnız tek faz araç:** go-e dışında Tesla, Vestel, Easee, ABB, Wallbox ve diğer varyantlar için tek faz onboard charger davranışı ve faz başına etkin güç ürün kılavuzunda açıkça doğrulanmalıdır. `charger.tek_faz_destegi=Hayır` bu soruyu tek başına cevaplamaz.
- **ABB Terra AC W22-SR-0:** Tek faz wallbox besleme desteği `Bilinmiyor`; monofaz ev senaryosu kesinleştirilemez.
- **Tesla özel şebeke topolojileri:** Gen 3 belgesi 230 V üç faz delta yapılandırmasında araç erişimi açısından özel sınırlama belirtir. Standart 400 V Wye sonucu bu topolojiye genellenmemelidir.
- **Vestel AC22 ve Pulsar Plus 22 kW:** Tek faz besleme desteği `Hayır` olsa da üç faz beslenen cihazın tek faz onboard charger taşıyan araçla davranışı mevcut pilot provenansında açık değildir.
- **Kablo varyantı:** Soketli wallboxlarda kullanılacak Type 2 kablonun faz/akım kapasitesi ayrı ürün olduğundan gerektiğinde ayrıca doğrulanmalıdır.

## Gelecek sürüme bırakılabilir

- `nominal_gerilim` ham metninden çıkarım yapmak yerine kaynaklı `tek_faz_nominal_gerilim_v` ve `uc_faz_fazlar_arasi_gerilim_v` alanlarının eklenmesi.
- Wallbox ürünleri için `tek_faz_aracla_uc_faz_beslemede_davranis` gibi ürün özel davranış alanı ve alan düzeyi provenansının eklenmesi.
- Konut için faz–nötr/fazlar-arası ölçüm, ana sigorta, eşzamanlı yük ve doğrulanmış kullanılabilir şarj gücü veri sözleşmesi.
- DLM'nin sayaç/modül modeli, ölçüm topolojisi, kurulum limiti ve devreye alma doğrulamasının ayrı yapılandırılmış alanlara ayrılması.
- Yerel şebeke işletmecisi ve ülke bazlı tek faz güç/faz dengesizliği kurallarının sürümlü mevzuat kaynağıyla tutulması.

## Kalan ana karar

KDS algoritması geliştirilmeden önce "güvenli ev kullanılabilir şarj gücü"nün hangi elektrikçi ölçümleri ve doğrulamalarla oluşturulacağı karara bağlanmalıdır. Bu değer belirlenmeden `arac_wallbox_etkin_guc_kw` yalnız araç–wallbox teorik üst sınırıdır.
