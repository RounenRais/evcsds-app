"""Adayları dört ayrı listeye ayırır. Girdi sırası korunur; sıralama yapılmaz."""

if __package__:
    from .hard_rules import apply_hard_rules, is_number
    from .metrics import calculate_metrics
else:
    from hard_rules import apply_hard_rules, is_number
    from metrics import calculate_metrics


def recommend_candidates(home, vehicle, user, wallboxes):
    result = {"eligible": [], "excluded": [], "needs_verification": [], "insufficient_data": []}
    groups = {"DEGERLENDIR": "eligible", "ELE": "excluded",
              "DOGRULAMA_GEREKLI": "needs_verification", "VERI_YETERSIZ": "insufficient_data"}
    ids = [wallbox.get("charger_id") for wallbox in wallboxes]
    if any(not isinstance(charger_id, str) or not charger_id.strip() for charger_id in ids):
        raise ValueError("NEED_INPUT: Her wallbox için gerçek charger_id gerekli.")
    if len(set(ids)) != len(ids):
        raise ValueError("Tekrarlı charger_id; alternatifler çift sayılmaz.")
    for wallbox in wallboxes:
        hard_rule = apply_hard_rules(home, vehicle, user, wallbox)
        item = {"charger_id": wallbox["charger_id"], "hard_rule": hard_rule}
        warnings = list(vehicle.get("kds_veri_uyarilari", [])) + list(wallbox.get("kds_veri_uyarilari", []))
        if not is_number(vehicle.get("wltp_tuketim_kwh_100km")):
            warnings.append("WLTP_EKSIK: Günlük enerji ihtiyacı tahmin edilmez.")
        if not is_number(user.get("gunluk_ortalama_km")):
            warnings.append("GUNLUK_KM_EKSIK: Günlük enerji hesaplanamaz.")
        if not is_number(user.get("evde_sarj_icin_uygun_sure_saat")):
            warnings.append("PARK_SURESI_EKSIK: İhtiyaç karşılama oranı hesaplanamaz.")
        if not is_number(user.get("butce_tl")):
            warnings.append("BUTCE_EKSIK: Opsiyonel bütçe eksik; teknik eleme nedeni değildir.")
        if not is_number(wallbox.get("fiyat_tl")):
            warnings.append("FIYAT_BILINMIYOR: Fiyat tahmini veya ekonomik oran üretilmez.")
        if wallbox.get("dinamik_yuk_yonetimi_destegi") in (None, "Bilinmiyor"):
            warnings.append("DLM_DOGRULAMA: DLM bilgisi doğrulanmalı; Bilinmiyor, Hayır değildir.")
        item["warnings"] = warnings
        if hard_rule["status"] == "DEGERLENDIR":
            item["metrics"] = calculate_metrics(home, vehicle, user, wallbox, hard_rule)
        result[groups[hard_rule["status"]]].append(item)
    return result
