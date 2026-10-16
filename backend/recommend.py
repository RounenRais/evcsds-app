"""Görsel analiz çıktısı ile karar motoru arasındaki köprü.

Motor (`kds_engine`) değiştirilmeden kullanılır. Bu modül yalnız üç iş yapar:
girdiyi motorun beklediği sözlüklere çevirir, sonucu arayüzün gösterebileceği
hale getirir ve kullanıcı onayı olmadan çalışmayı reddeder.
"""

from __future__ import annotations

from typing import Any

import catalog
from kds_engine.engine import recommend_candidates


GRUP_ADLARI = {
    "eligible": "uygun",
    "excluded": "elenen",
    "needs_verification": "dogrulanmali",
    "insufficient_data": "veri_yetersiz",
}

GECERLI_FAZLAR = {"monofaz", "trifaz", "belirsiz"}
# Motorun `hard_rules.apply_hard_rules` içinde birebir karşılaştırdığı değerler.
GECERLI_KURULUM_YERLERI = {"İç mekan", "Dış mekan"}

HR08_UYARISI = (
    "Sözleşme gücü ve tüketim, tesisatın güvenli şarj gücünü kanıtlamaz. "
    "Pano, hat ve korumalar yetkili bir elektrik tesisatçısı tarafından ayrıca "
    "doğrulanmalıdır. Bu sistem kurulum onayı vermez."
)


class OneriGirdiHatasi(ValueError):
    """Girdi motorun çalıştırılamayacağı kadar eksik veya tutarsız."""


def _ev_girdisi(home: dict[str, Any]) -> dict[str, Any]:
    faz = home.get("faz")
    if faz not in GECERLI_FAZLAR:
        raise OneriGirdiHatasi(
            "Ev fazı 'monofaz', 'trifaz' veya 'belirsiz' olmalıdır."
        )
    # Motor yalnız `faz` alanını okur; diğerleri sonucun izlenebilirliği için
    # taşınır ve çıktıda geri verilir.
    return {
        "faz": faz,
        "sozlesme_gucu_kw": home.get("sozlesme_gucu_kw"),
        "donem_tuketimi_kwh": home.get("donem_tuketimi_kwh"),
        "gunluk_ortalama_kwh": home.get("gunluk_ortalama_kwh"),
        "tarife": home.get("tarife"),
    }


def _kullanici_girdisi(user: dict[str, Any]) -> dict[str, Any]:
    yer = user.get("kurulum_yeri")
    if yer not in GECERLI_KURULUM_YERLERI:
        raise OneriGirdiHatasi("Kurulum yeri 'İç mekan' veya 'Dış mekan' olmalıdır.")
    return {
        "gunluk_ortalama_km": user.get("gunluk_ortalama_km"),
        "evde_sarj_icin_uygun_sure_saat": user.get("evde_sarj_icin_uygun_sure_saat"),
        "butce_tl": user.get("butce_tl"),
        "kurulum_yeri": yer,
    }


def _aday_sunumu(aday: dict[str, Any]) -> dict[str, Any]:
    """Motor çıktısına ürünün tanıtım alanlarını ekler; metrikleri değiştirmez."""
    hard_rule = aday.get("hard_rule", {})
    return {
        "charger_id": aday["charger_id"],
        "urun": catalog.wallbox_ozeti(aday["charger_id"]),
        "durum": hard_rule.get("status"),
        "gerekceler": hard_rule.get("reasons", []),
        "kurallar": hard_rule.get("rules", []),
        "eksik_alanlar": hard_rule.get("kds_eksik_alanlar", []),
        "uyarilar": aday.get("warnings", []),
        "metrikler": aday.get("metrics"),
    }


def oneri_uret(
    home: dict[str, Any],
    vehicle_id: str,
    user: dict[str, Any],
    kullanici_onayladi: bool,
) -> dict[str, Any]:
    """Onaylanmış ev girdisi + araç + kullanım bilgisinden dört aday listesi üretir.

    `kullanici_onayladi` bilerek zorunludur: görsel analiz çıktısı
    `kdsye_dogrudan_aktarilabilir=False` döndürür, yani otomatik okunan hiçbir
    değer kullanıcı doğrulamadan karar verisi sayılamaz.
    """
    if not kullanici_onayladi:
        raise OneriGirdiHatasi(
            "Ev bilgileri kullanıcı tarafından onaylanmadan öneri üretilemez."
        )

    arac = catalog.arac_getir(vehicle_id)
    if arac is None:
        raise OneriGirdiHatasi(f"Katalogda böyle bir araç yok: {vehicle_id}")

    ev = _ev_girdisi(home)
    kullanici = _kullanici_girdisi(user)
    wallboxlar = list(catalog.wallboxlar().values())

    sonuc = recommend_candidates(ev, arac, kullanici, wallboxlar)

    gruplar = {
        yeni_ad: [_aday_sunumu(aday) for aday in sonuc[eski_ad]]
        for eski_ad, yeni_ad in GRUP_ADLARI.items()
    }
    sayilar = {ad: len(adaylar) for ad, adaylar in gruplar.items()}

    return {
        "girdi": {
            "home": ev,
            "arac": {
                "vehicle_id": arac["vehicle_id"],
                "marka": arac.get("marka"),
                "model": arac.get("model"),
                "ac_tek_faz_azami_guc_kw": arac.get("ac_tek_faz_azami_guc_kw"),
                "ac_uc_faz_azami_guc_kw": arac.get("ac_uc_faz_azami_guc_kw"),
                "wltp_tuketim_kwh_100km": arac.get("wltp_tuketim_kwh_100km"),
            },
            "user": kullanici,
        },
        "sayilar": sayilar,
        "toplam_degerlendirilen": sum(sayilar.values()),
        "gruplar": gruplar,
        "siralama_yapilmadi": True,
        "uyari": HR08_UYARISI,
    }
