# KDS TOPSIS Karar Matrisi Sözleşmesi V1

**Tarih:** 2026-09-27

## Matris tanımı

- Satır: hard-rule sonrası `DEGERLENDIR` durumunda kalan wallbox alternatifi.
- Sütun: önceden seçilmiş ve aynı deneyde gözlenebilir soft kriter.
- `a_ij`: alternatif `i` için kriter `j` değeri.
- Kriter yönü: `KDS_KRITER_ADAYLARI_V1.xlsx` içindeki benefit/cost tanımı.
- Ağırlık: sürümlü, tutarlılığı kontrol edilmiş haricî AHP/uzman ağırlık seti; bu pakette değer yoktur.

## Matrise girmeyen alanlar

`kds_veri_kullanilabilir`, Type 2 uyumu, temel monofaz/trifaz çalışabilirliği, açık iç/dış mekân uyumsuzluğu ve RCD/RDC-DD kurulum yapısı puan sütunu değildir. İlk grup hard-rule/veri yeterliliği katmanında; koruma alanları koşullu kurulum açıklamasında ele alınır.

## Ön koşullar

1. Track ve aday havuzu sabittir.
2. Hard-rule sonuçları ve eleme nedenleri saklanmıştır.
3. Kriter seti, yönler ve ağırlık seti sürümlüdür.
4. Matris sayısaldır; `null` veya `Bilinmiyor` içermez. Bunun yolu imputasyon değil, V1 eksik-veri politikasını uygulamaktır.
5. Aynı kriterin birim ve hesaplama yöntemi bütün alternatiflerde aynıdır.

## Gelecekteki hesaplama sözleşmesi

Standart TOPSIS uygulanacaksa vektör normalizasyonu, ağırlıklı normalize matris, benefit/cost ideal çözümleri, ideal uzaklıklar ve yakınlık katsayısı yöntem sürümünde açıkça kaydedilir:

```text
r_ij = a_ij / sqrt(sum_i(a_ij^2))
v_ij = w_j × r_ij
C_i  = S_i_minus / (S_i_plus + S_i_minus)
```

Sıfır norm, sabit sütun veya tanımsız payda oluşursa çalışma durdurulup veri/kriter kontrolü yapılır; sessiz düzeltme yapılmaz.

## Skorun anlamı

`C_i` yalnız seçili kriterler, ağırlıklar, aday havuzu ve normalizasyon altında göreli yakınlık katsayısıdır. Güvenlik olasılığı, doğruluk olasılığı, OCR confidence veya “% güvenli” değildir. Farklı track/kriter/ağırlık setlerinde oluşan katsayılar doğrudan karşılaştırılmaz.

## Çıktı izleri

Her koşuda `run_id`, track, aday havuzu, hard-rule sürümü, kriter seti, ağırlık seti, matris, normalizasyon yöntemi, skor/sıra ve açıklama sözleşmesi sürümü saklanmalıdır. Bu belge hesaplama çalıştırmaz.
