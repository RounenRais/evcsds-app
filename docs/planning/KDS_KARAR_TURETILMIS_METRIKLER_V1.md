# KDS Karar Türetilmiş Metrikler V1

**Tarih:** 2026-09-27  
**Metrik sayısı:** 6

Bu sözlük puan veya sıralama üretmez. Metrikler yalnız hard-rule sonrası teknik bağlamı belirlenmiş alternatiflerde ve belirtilen ön koşullar sağlandığında hesaplanır.

## M01 — Günlük araç enerji ihtiyacı

**Alan:** `gunluk_arac_enerji_ihtiyaci_kwh`

```text
E_daily = user.gunluk_ortalama_km
          × vehicle.wltp_tuketim_kwh_100km / 100
```

WLTP tüketimi veya günlük km yoksa sonuç `null` kalır. Batarya kapasitesi/menzilden tahmin yapılmaz. Değer, araç bataryasına teorik günlük enerji ihtiyacıdır; şebekeden çekilecek kayıplı enerji değildir.

## M02 — Teorik araç–wallbox etkin AC güç

**Alan:** `arac_wallbox_teorik_etkin_guc_kw`

- Monofaz yol açık ve kanıtlıysa: `min(vehicle.ac_tek_faz_azami_guc_kw, charger.tek_faz_azami_guc_kw)`.
- Trifaz yol açık ve kanıtlıysa: `min(vehicle.ac_uc_faz_azami_guc_kw, charger.uc_faz_azami_guc_kw)`.
- Üç faz wallbox + yalnız tek faz araç çapraz durumunda ürün özel davranışı ve gerilim kanıtı yoksa sonuç `null`, durum `DOGRULAMA_GEREKLI` olur.

Bu değer konutun güvenli tesisat gücü değildir ve `home.sozlesme_gucu_kw` ile minimum alınmaz.

## M03 — Teorik günlük ihtiyaç karşılama süresi

**Alan:** `teorik_gunluk_ihtiyac_karsilama_suresi_saat`

```text
T_theoretical = E_daily / P_effective
```

M01 veya M02 `null`, ya da `P_effective ≤ 0` ise sonuç `null` olur. Bu metrik kaynaklandırılmamış şarj verimi katsayısı kullanmaz ve eski verim katsayılı değişkenden ayrı tutulur. Sabit güç, batarya kabul eğrisi ve kayıpları göz ardı ettiği için gerçek şarj süresi değil; yalnız teorik karşılaştırma değeridir.

## M04 — Park süresine göre ihtiyaç karşılama oranı

**Alan:** `gunluk_ihtiyac_karsilama_orani`

```text
coverage_ratio = min(1,
                     P_effective × user.evde_sarj_icin_uygun_sure_saat
                     / E_daily)
```

Boyutsuzdur. `1`, teorik günlük ihtiyacın mevcut park süresinde nominal sabit güç varsayımıyla karşılanabildiğini gösterir; enerji kayıplarını ve ev tesisatı kapasitesini içermez. `E_daily ≤ 0` ise bölme yapılmaz; oran `null` ve “günlük ihtiyaç yok/hesap uygulanamaz” durumu ayrı tutulur. **Kriter adayıdır; nihai kriter değildir.**

## M05 — Nominal kapasite kullanım oranı

**Alan:** `nominal_kapasite_kullanim_orani`

```text
utilisation_ratio = P_effective / charger.nominal_azami_guc_kw
```

Payda pozitif ve M02 doluysa hesaplanır. Aracın seçili wallboxın nominal kapasitesinin ne kadarından yararlanabildiğini anlatır. Yüksek oran her zaman daha iyi ürün anlamına gelmez; gelecekte araç değişimi veya kapasite rezervini kapsamaz. Bu nedenle otomatik benefit kriteri yapılmaz; tanısal/kriter adayıdır.

## M06 — Bütçe oranı

**Alan:** `fiyat_butce_orani`

```text
price_budget_ratio = charger.fiyat_tl / user.butce_tl
```

Yalnız iki değer de dolu ve bütçe pozitifse hesaplanır. Fiyat veya bütçe yoksa `null`; fiyat tahmini, yabancı para dönüşümü veya ortalama ataması yapılmaz. Yalnız Track B ekonomik alt deneyinde koşullu kriter adayıdır.

## Ortak guardrail

Metriklerin hiçbiri kurulum güvenliği, pano yeterliliği veya ürün doğruluk olasılığı değildir. Bir metrik `null` ise `0` puana dönüştürülmez.
