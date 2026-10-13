"""M01–M06: bilinmeyen girdiler None kalır; metrikler puan veya sıralama değildir."""

if __package__:
    from .hard_rules import apply_hard_rules, get_phase_path, is_number, is_positive
else:
    from hard_rules import apply_hard_rules, get_phase_path, is_number, is_positive


def calculate_daily_energy(user, vehicle):
    km = user.get("gunluk_ortalama_km")
    consumption = vehicle.get("wltp_tuketim_kwh_100km")
    if not is_number(km) or not is_number(consumption) or km < 0 or consumption < 0:
        return None
    return km * consumption / 100


def calculate_effective_power(home, vehicle, user, wallbox, hard_rule_result=None):
    result = hard_rule_result
    if result is None:
        result = apply_hard_rules(home, vehicle, user, wallbox)
    if result["status"] != "DEGERLENDIR":
        return None
    path = get_phase_path(home, vehicle, wallbox)
    if path in ("tek_faz", "goe_capraz_tek_faz"):
        return min(vehicle["ac_tek_faz_azami_guc_kw"], wallbox["tek_faz_azami_guc_kw"])
    if path == "uc_faz":
        return min(vehicle["ac_uc_faz_azami_guc_kw"], wallbox["uc_faz_azami_guc_kw"])
    return None


def calculate_theoretical_time(daily_energy, effective_power):
    if not is_number(daily_energy) or daily_energy < 0 or not is_positive(effective_power):
        return None
    return daily_energy / effective_power


def calculate_coverage_ratio(daily_energy, effective_power, available_hours):
    if not is_positive(daily_energy) or not is_positive(effective_power):
        return None
    if not is_number(available_hours) or available_hours < 0:
        return None
    return min(1, effective_power * available_hours / daily_energy)


def calculate_utilisation_ratio(effective_power, nominal_power):
    if not is_positive(effective_power) or not is_positive(nominal_power):
        return None
    return effective_power / nominal_power


def calculate_price_budget_ratio(wallbox, user):
    price = wallbox.get("fiyat_tl")
    budget = user.get("butce_tl")
    if not is_number(price) or price < 0 or not is_positive(budget):
        return None
    return price / budget


def calculate_metrics(home, vehicle, user, wallbox, hard_rule_result=None):
    energy = calculate_daily_energy(user, vehicle)
    power = calculate_effective_power(home, vehicle, user, wallbox, hard_rule_result)
    return {
        "gunluk_arac_enerji_ihtiyaci_kwh": energy,
        "arac_wallbox_teorik_etkin_guc_kw": power,
        "teorik_gunluk_ihtiyac_karsilama_suresi_saat": calculate_theoretical_time(energy, power),
        "gunluk_ihtiyac_karsilama_orani": calculate_coverage_ratio(
            energy, power, user.get("evde_sarj_icin_uygun_sure_saat")),
        "nominal_kapasite_kullanim_orani": calculate_utilisation_ratio(power, wallbox.get("nominal_azami_guc_kw")),
        "fiyat_butce_orani": calculate_price_budget_ratio(wallbox, user),
    }
