"""HR01–HR08: ürün uygunluğu; elektrik tesisatı için kurulum onayı değildir."""

from math import isfinite


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def is_positive(value):
    return is_number(value) and value > 0


def is_unknown(value):
    return value is None or value in ("", "Bilinmiyor")


def phase_limits_present(record, power_field, current_field):
    return is_positive(record.get(power_field)) and is_positive(record.get(current_field))


def get_phase_path(home, vehicle, wallbox):
    """Kanıtlı araç–wallbox yolunu seçer. Eksik kanıtta None; gerilim metni ayrıştırılmaz."""
    if home.get("faz") == "monofaz" and wallbox.get("tek_faz_destegi") == "Evet":
        if vehicle.get("ac_tek_faz_destegi") == "Evet":
            if (phase_limits_present(vehicle, "ac_tek_faz_azami_guc_kw", "ac_tek_faz_azami_akim_a")
                    and phase_limits_present(wallbox, "tek_faz_azami_guc_kw", "tek_faz_azami_akim_a")):
                return "tek_faz"
    elif home.get("faz") == "trifaz" and wallbox.get("uc_faz_destegi") == "Evet":
        if not phase_limits_present(wallbox, "uc_faz_azami_guc_kw", "uc_faz_faz_basina_akim_a"):
            return None
        if vehicle.get("ac_uc_faz_destegi") == "Evet":
            if phase_limits_present(vehicle, "ac_uc_faz_azami_guc_kw", "ac_uc_faz_faz_basina_akim_a"):
                return "uc_faz"
        elif vehicle.get("ac_uc_faz_destegi") == "Hayır" and vehicle.get("ac_tek_faz_destegi") == "Evet":
            # Paket teknik eşleşme taslağı §5–§9 ve TC-13: yalnız bu ürün için
            # 3,7 kW tek faz araç davranışı belgelenmiş. Akımdan yeni kW türetilmez.
            if (wallbox.get("charger_id") == "GOE_CHARGER_GEMINI_11_TR"
                    and wallbox.get("nominal_gerilim") == "230/240 V tek faz / 400/415 V üç faz"
                    and wallbox.get("tek_faz_destegi") == "Evet"
                    and wallbox.get("tek_faz_azami_guc_kw") == 3.7
                    and wallbox.get("uc_faz_faz_basina_akim_a") == 16
                    and phase_limits_present(wallbox, "tek_faz_azami_guc_kw", "tek_faz_azami_akim_a")
                    and phase_limits_present(vehicle, "ac_tek_faz_azami_guc_kw", "ac_tek_faz_azami_akim_a")):
                return "goe_capraz_tek_faz"
    return None


def apply_hard_rules(home, vehicle, user, wallbox):
    rules = []
    reasons = []

    def record(rule_id, status, reason):
        rules.append({"rule_id": rule_id, "status": status, "reason": reason})
        if status != "DEGERLENDIR" or rule_id == "HR08":
            reasons.append(reason)

    if wallbox.get("kds_veri_kullanilabilir") != "Evet":
        record("HR01", "VERI_YETERSIZ", "Katalog kullanılabilirlik kanıtı yok veya Hayır; kayıt değerlendirilmez.")
        return {"status": "VERI_YETERSIZ", "rules": rules, "reasons": reasons,
                "kds_eksik_alanlar": wallbox.get("kds_eksik_alanlar", []),
                "kds_veri_uyarilari": wallbox.get("kds_veri_uyarilari", [])}
    record("HR01", "DEGERLENDIR", "Katalog kullanılabilirlik kapısı geçti.")

    vehicle_connector = vehicle.get("ac_konnektor_tipi")
    charger_connector = wallbox.get("ac_konnektor_tipi")
    if is_unknown(vehicle_connector) or is_unknown(charger_connector):
        record("HR02", "DOGRULAMA_GEREKLI", "AC konektör bilgisi eksik veya Bilinmiyor.")
    elif vehicle_connector != charger_connector:
        record("HR02", "ELE", "Araç ve wallbox AC konektörleri açıkça farklı.")
    else:
        record("HR02", "DEGERLENDIR", "AC konektörleri eşleşiyor.")

    phase = home.get("faz")
    if phase == "monofaz":
        if wallbox.get("tek_faz_destegi") == "Hayır":
            record("HR03", "ELE", "Monofaz evde seçili wallboxın tek faz besleme desteği Hayır.")
        elif (wallbox.get("tek_faz_destegi") != "Evet"
              or not phase_limits_present(wallbox, "tek_faz_azami_guc_kw", "tek_faz_azami_akim_a")):
            record("HR03", "DOGRULAMA_GEREKLI", "Wallbox tek faz besleme desteği veya güç/akım sınırı doğrulanmalı.")
        else:
            record("HR03", "DEGERLENDIR", "Wallboxın tek faz besleme yolu açık.")
    elif phase == "trifaz":
        if (wallbox.get("uc_faz_destegi") == "Evet"
                and phase_limits_present(wallbox, "uc_faz_azami_guc_kw", "uc_faz_faz_basina_akim_a")):
            record("HR04", "DEGERLENDIR", "Wallboxın üç faz besleme yolu açık.")
        else:
            record("HR04", "DOGRULAMA_GEREKLI", "Üç faz yolu veya tek faz kurulumun faz dengesi/saha koşulları doğrulanmalı.")
    else:
        record("HR05", "DOGRULAMA_GEREKLI", "Ev fazı belirsiz veya eksik; faza bağlı güç hesaplanmaz.")

    location = user.get("kurulum_yeri")
    if location == "İç mekan":
        suitability = wallbox.get("ic_mekan_uygun")
    elif location == "Dış mekan":
        suitability = wallbox.get("dis_mekan_uygun")
    else:
        suitability = None
    if suitability == "Hayır":
        record("HR06", "ELE", "Ürün seçilen kurulum yerine açıkça uygun değil.")
    elif suitability != "Evet":
        record("HR06", "DOGRULAMA_GEREKLI", "Kurulum yeri veya ilgili ürün uygunluğu doğrulanmalı; IP sınıfından türetilmez.")
    else:
        record("HR06", "DEGERLENDIR", "Ürünün seçilen kurulum yeri uygunluğu Evet.")

    if get_phase_path(home, vehicle, wallbox) is None:
        record("HR07", "DOGRULAMA_GEREKLI", "Araç faz yolu, faza özel sınırlar veya çapraz faz ürün kanıtı yetersiz.")
    else:
        record("HR07", "DEGERLENDIR", "Araç–wallbox faz yolu kanıtlı; bu durum ev tesisatı onayı değildir.")
    record("HR08", "DEGERLENDIR", "Sözleşme gücü/tüketim güvenli güç sınırı değildir; pano, hat ve korumalar ayrıca doğrulanmalıdır.")

    status = "DEGERLENDIR"
    if any(rule["status"] == "ELE" for rule in rules):
        status = "ELE"
    elif any(rule["status"] == "DOGRULAMA_GEREKLI" for rule in rules):
        status = "DOGRULAMA_GEREKLI"
    return {"status": status, "rules": rules, "reasons": reasons,
            "kds_eksik_alanlar": wallbox.get("kds_eksik_alanlar", []),
            "kds_veri_uyarilari": wallbox.get("kds_veri_uyarilari", [])}
