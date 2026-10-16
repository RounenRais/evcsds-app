# KDS AHP Ağırlıklandırma Spesifikasyonu V1

**Tarih:** 2026-09-27

## Rol

AHP'nin görevi teknik uygunluğu belirlemek değildir. AHP, hard-rule sonrası seçilmiş **soft karar kriterlerinin** paydaş yargılarına dayalı göreli ağırlıklarını üretmek için kullanılabilir.

- Matris kriter seviyesindedir.
- 30 wallbox alternatifi birbirleriyle AHP pairwise karşılaştırılmaz.
- Güvenlik, konektör, faz çalışabilirliği veya açık kurulum yeri uyumsuzluğu AHP ağırlığıyla telafi edilemez.
- AHP'den elde edilecek `w_j` ağırlıkları daha sonra TOPSIS veya aynı kriter setini kullanan başka bir yöntemle kullanılabilir.
- Bu pakette ikili karşılaştırma değeri ve ağırlık üretilmemiştir.

## Veri toplama sırası

1. Track A veya Track B seçilir.
2. Eksik-veri politikası sabitlenir.
3. Nihai kriter seti aday sözlüğünden seçilir.
4. Kriter tanımları katılımcılara aynı biçimde sunulur.
5. Her karşılaştırma için kişi/grup, tarih ve gerekçe kaydedilir.
6. Matris tamamlandıktan sonra ağırlık ve tutarlılık hesaplanır.

## Tutarlılık

```text
CI = (lambda_max - n) / (n - 1)
CR = CI / RI
```

`CR < 0,10` metodolojik hedef olarak kullanılır. Eşik sağlanmazsa yargılar gözden geçirilir; tutarsızlığı gizlemek için matris hücreleri otomatik değiştirilmez. Birden fazla katılımcının yargılarını birleştirme yöntemi çalışmadan önce ön-kayıt altına alınmalıdır.

## Sürümleme

Ağırlık çıktısı ileride `weight_set_id`, track, kriter listesi, katılımcı kapsamı, tarih, CI, CR ve kaynak şablon sürümüyle saklanmalıdır. Farklı track veya kriter setlerinin ağırlıkları birbirinin yerine kullanılmaz.
