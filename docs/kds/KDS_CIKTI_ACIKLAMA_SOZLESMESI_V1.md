# KDS Çıktı Açıklama Sözleşmesi V1

**Tarih:** 2026-09-27

## Amaç

Gelecekteki karar motoru yalnız sıra/skor değil, sonucu yeniden incelemeye yetecek gerekçe ve uyarıları da üretmelidir. Çıktı üç ayrı liste taşır: `ranked_alternatives`, `excluded_alternatives`, `needs_verification`.

## Sıralanan alternatif alanları

- `charger_id`, `urun_adi`
- `sira` — yalnız aynı koşudaki değerlendirilmiş alternatifler arasında
- `method`, `method_score`, `track`, `candidate_pool_id`
- `kullanilan_kriterler` ve kriter değerleri
- `arac_wallbox_teorik_etkin_guc_kw`
- `gunluk_arac_enerji_ihtiyaci_kwh`
- `gunluk_ihtiyac_karsilama_orani` veya hesaplanamama nedeni
- `olumlu_gerekceler`
- `trade_off_dezavantajlar`
- `uyarilar`
- `fiyat_durumu`, `teknik_veri_durumu`
- kullanılan veri/kural/kriter/ağırlık sürümleri

Fiyat bilinmiyorsa açık `FIYAT_BILINMIYOR` uyarısı üretilir; fiyat tahmini yapılmaz. Teknik alan bilinmiyorsa alan adı ve beklenen doğrulama kaynağı gösterilir.

## Elenen veya değerlendirilemeyen alternatifler

Her kayıt `charger_id`, `hard_rule_status`, `rule_id`, `neden`, `eksik_alanlar` ve `kullaniciya_mesaj` taşır. `sira` ve `method_score` null olur. `VERI_YETERSIZ`, “kötü ürün” mesajına dönüştürülmez.

## Skor dili

TOPSIS yakınlık katsayısı veya başka yöntem skoru için “%87 güvenli”, “%92 doğru”, “%90 uyumlu” gibi olasılık/sertifika dili kullanılmaz. Skor yalnız aynı koşudaki göreli yöntem değeridir. Kurulum güvenliği ayrıca yetkili elektrikçi doğrulaması ister.

## Kavramsal örnek

```json
{
  "run_id": "<kimlik>",
  "track": "A|B",
  "ranked_alternatives": [
    {
      "charger_id": "<id>",
      "urun_adi": "<marka model>",
      "sira": null,
      "method_score": null,
      "kullanilan_kriterler": [],
      "olumlu_gerekceler": [],
      "trade_off_dezavantajlar": [],
      "uyarilar": []
    }
  ],
  "excluded_alternatives": [],
  "needs_verification": []
}
```

Örnek sözleşme yapısını gösterir; gerçek ürün sonucu, sıra, puan veya ağırlık içermez.
