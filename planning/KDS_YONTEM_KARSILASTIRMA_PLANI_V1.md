# KDS Yöntem Karşılaştırma Planı V1

**Tarih:** 2026-09-27  
**Durum:** Gelecekte uygulanacak deney planı; bu pakette yöntem çalıştırılmamıştır.

## Karşılaştırma adayları

| Kimlik | Sistem | Rol |
|---|---|---|
| B0 | Yalnız hard rules | Teknik durum ve uyarı üretir; sıralama yoktur. |
| B1 | Hard rules + basit weighted sum / SMART-benzeri baseline | Aynı soft kriterleri haricî, önceden tanımlı ağırlıklarla birleştiren basit referans yöntemdir. Bu pakette ağırlık yoktur. |
| M1 | Hard rules + AHP kriter ağırlıkları + TOPSIS | AHP kriter ağırlığını, TOPSIS alternatif sıralamasını sağlar; roller rakip değildir. |
| M2 | Aynı hard rules, kriterler ve ağırlıklarla VIKOR veya ELECTRE | İsteğe bağlı yöntem duyarlılığı/araştırma uzantısıdır. |

## Adil karşılaştırma koşulları

- Aynı D1–D4 senaryoları, aynı hard-rule sürümü ve aynı başlangıç havuzu kullanılır.
- Sıralamalı yöntemlerde aynı kriter seti, eksik-veri politikası ve ağırlık seti kullanılır.
- Track A ve Track B sonuçları karıştırılmaz.
- B0 sıralama üretmediği için başarı ölçütü teknik durum/uyarı doğruluğudur; sıralama korelasyonu beklenmez.
- B1 ağırlıkları gelecek deney protokolünde önceden ilan edilir; bu belgede eşit veya başka ağırlık atanmaz.

## D1–D4 ölçüm planı

- **D1:** Geçerli çıktı üretme oranı, sıralama kararlılığı, açıklama kapsamı; uzman değerlendirmesi varsa top-N uygunluğu.
- **D2:** Günlük ihtiyaç/park süresi değiştiğinde teorik metrik ve sıralama duyarlılığı; monotonluk/duyarlılık kontrolleri.
- **D3:** Eksik değeri uydurmama, doğru `VERI_YETERSIZ`/`DOGRULAMA_GEREKLI` üretme, temiz–bozulmuş çiftte açıklama farkı.
- **D4:** Hard-rule sonucu ve gerekçesinin beklenen teknik davranışla eşleşmesi; açık uyumsuzluğun soft kriterle geri dönmemesi.

## Raporlanacak yöntem düzeyi göstergeler

Kapsama oranı, değerlendirilemeyen alternatif oranı, hard-rule durum eşleşmesi, açıklama/uyarı doğruluğu, top-N örtüşmesi (uzman referansı varsa), sıra korelasyonu ve ağırlık/kriter duyarlılığı. Bu ölçütler için hedef değerler henüz belirlenmemiştir.

## Temel metodolojik not

AHP ile TOPSIS birbirinin alternatifi değildir: AHP kriter ağırlığı üretir; TOPSIS alternatifleri bu ağırlıklarla göreli olarak sıralar. Alternatif yöntem karşılaştırması TOPSIS–weighted sum–VIKOR/ELECTRE arasında, aynı koşullar altında yapılır.
