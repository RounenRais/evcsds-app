"""Çalıştırma: python -m kds_engine.run_benchmark (yalnız standart kütüphane)."""

import argparse
import copy
import csv
import json
from collections import Counter
from math import isclose
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

if __package__:
    from .engine import recommend_candidates
    from .metrics import calculate_daily_energy
else:
    from engine import recommend_candidates
    from metrics import calculate_daily_energy


ROOT = Path(__file__).resolve().parents[1]
GROUPS = {"eligible": "eligible_count", "excluded": "excluded_count",
          "needs_verification": "verification_count", "insufficient_data": "insufficient_data_count"}


def read_json(path):
    with path.open(encoding="utf-8-sig") as handle:
        return json.load(handle)


def read_test_table(path):
    """Kaynak teknik test tablosunu Excel dosyasından okur."""
    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as archive:
        strings = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            strings = ["".join(node.itertext()) for node in root.findall("s:si", ns)]
        root = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in root.findall("s:sheetData/s:row", ns):
        values = {}
        for cell in row.findall("s:c", ns):
            index = 0
            for letter in cell.attrib["r"]:
                if letter.isalpha():
                    index = index * 26 + ord(letter.upper()) - ord("A") + 1
            value_node = cell.find("s:v", ns)
            value = None if value_node is None else value_node.text
            kind = cell.attrib.get("t")
            if kind == "inlineStr":
                value = "".join(node.text or "" for node in cell.findall("s:is//s:t", ns))
            elif kind == "s":
                value = strings[int(value)]
            elif value is not None:
                value = float(value)
            values[index - 1] = value
        rows.append(values)
    headers = rows[0]
    return [{name: row.get(index) for index, name in headers.items()} for row in rows[1:]]


def index_records(records, field):
    index = {}
    for record in records:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip() or value in index:
            raise ValueError(f"NEED_INPUT: Eksik/tekrarlı {field}: {value!r}")
        index[value] = record
    return index


def load_inputs(root):
    paths = {
        "vehicles": root / "data/ARAC_KDS_CEKIRDEK_100.json",
        "wallboxes": root / "data/WALLBOX_KDS_CEKIRDEK_30_V1_1.json",
        "pools": root / "data/KDS_ADAY_HAVUZLARI_V1.json",
        "homes": root / "data/KDS_EV_PROFILLERI_V1.json",
        "scenarios": root / "data/KDS_BENCHMARK_D1_D4.json",
        "tests": root / "data/KDS_TEKNIK_ESLESME_TEST_VAKALARI.xlsx",
    }
    for path in paths.values():
        if not path.is_file():
            raise ValueError(f"NEED_INPUT: Kaynak bulunamadı: {path}")
    vehicles = index_records(read_json(paths["vehicles"]), "vehicle_id")
    wallboxes = index_records(read_json(paths["wallboxes"]), "charger_id")
    homes = index_records(read_json(paths["homes"]), "home_profile_id")
    scenarios = read_json(paths["scenarios"])
    index_records(scenarios, "scenario_id")
    tests = index_records(read_test_table(paths["tests"]), "test_id")
    pools = index_records(read_json(paths["pools"])["havuzlar"], "candidate_pool_id")
    if len(vehicles) != 100 or len(wallboxes) != 30:
        raise ValueError("NEED_INPUT: Kaynak kayıt sayıları 100 araç / 30 wallbox değil.")
    if Counter(s["dataset_id"] for s in scenarios) != {"D1": 25, "D2": 20, "D3": 20, "D4": 20}:
        raise ValueError("NEED_INPUT: D1–D4 sayıları 25/20/20/20 değil.")
    for pool in pools.values():
        ids = pool["charger_ids"]
        if len(ids) != pool["uye_sayisi"] or len(ids) != len(set(ids)) or not set(ids) <= wallboxes.keys():
            raise ValueError(f"Geçersiz havuz üyeliği: {pool['candidate_pool_id']}")
    technical = pools["POOL_TEKNIK_27"]["charger_ids"]
    if len(technical) != 27 or any(wallboxes[c]["kds_veri_kullanilabilir"] != "Evet" for c in technical):
        raise ValueError("Teknik havuz kullanılabilirlik kontrolü başarısız.")
    for scenario in scenarios:
        for field, index in (("vehicle_id", vehicles), ("home_profile_id", homes), ("candidate_pool_id", pools)):
            if scenario.get(field) not in index:
                raise ValueError(f"NEED_INPUT: {scenario['scenario_id']} için geçersiz {field}")
        focus = scenario.get("focus_charger_id")
        if focus and focus not in pools[scenario["candidate_pool_id"]]["charger_ids"]:
            raise ValueError(f"Odak ürün havuzda yok: {scenario['scenario_id']}")
        test = scenario.get("source_test_id")
        if test and test not in tests:
            raise ValueError(f"NEED_INPUT: Teknik test bulunamadı: {test}")
        parent = scenario.get("parent_scenario_id")
        if parent and parent not in {s["scenario_id"] for s in scenarios}:
            raise ValueError(f"Eksik temiz senaryo: {parent}")
    return paths, vehicles, wallboxes, homes, scenarios, tests, pools


def scenario_inputs(scenario, homes, vehicles):
    home = copy.deepcopy(homes[scenario["home_profile_id"]])
    # Bağımsız kullanıcı tablosu yok; alanlar doğrudan senaryo kaydında mevcut.
    user = {"user_profile_id": scenario["user_profile_id"]}
    for field in ("gunluk_ortalama_km", "evde_sarj_icin_uygun_sure_saat", "butce_tl", "kurulum_yeri"):
        key = "user_" + field
        if key not in scenario:
            raise ValueError(f"NEED_INPUT: Senaryoda {key} bulunamadı.")
        user[field] = scenario[key]
    vehicle = copy.deepcopy(vehicles[scenario["vehicle_id"]])
    override = scenario.get("scenario_override", {})
    if not isinstance(override, dict) or set(override) - {"home", "vehicle", "user"}:
        raise ValueError("NEED_INPUT: Desteklenmeyen scenario_override yapısı.")
    home.update(override.get("home", {}))
    vehicle.update(override.get("vehicle", {}))
    user.update(override.get("user", {}))
    # Düzleştirilmiş alanlar katalog yerine kullanılmaz; tutarlılığı doğrulanır.
    for field in ("faz", "sozlesme_gucu_kw", "donem_tuketimi_kwh", "gunluk_ortalama_kwh", "tarife"):
        if scenario["home_" + field] != home.get(field):
            raise ValueError(f"Ev snapshot farkı: {scenario['scenario_id']} / {field}")
    if scenario["vehicle_wltp_tuketim_kwh_100km"] != vehicle.get("wltp_tuketim_kwh_100km"):
        raise ValueError(f"Araç snapshot farkı: {scenario['scenario_id']}")
    return home, vehicle, user


def same_number(actual, expected):
    if actual is None or expected is None:
        return actual is expected
    return isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9)


def check_scenario(scenario, candidates, user, vehicle, tests):
    checks = []

    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    all_items = [item for items in candidates.values() for item in items]
    check("Her alternatif tam bir listeye ayrıldı", len({i["charger_id"] for i in all_items}) == len(all_items))
    for group, expected in (("eligible", "DEGERLENDIR"), ("excluded", "ELE"),
                            ("needs_verification", "DOGRULAMA_GEREKLI"), ("insufficient_data", "VERI_YETERSIZ")):
        check(group + " statü ayrımı", all(i["hard_rule"]["status"] == expected for i in candidates[group]))
    check("ELE kuralı eligible listesine geçmedi", all(
        not any(r["status"] == "ELE" for r in i["hard_rule"]["rules"]) for i in candidates["eligible"]))
    energy = calculate_daily_energy(user, vehicle)
    check("M01 kaynak senaryo değeriyle eşleşiyor", same_number(energy, scenario["gunluk_arac_enerji_ihtiyaci_kwh"]))
    for item in candidates["eligible"]:
        metrics = item["metrics"]
        check(item["charger_id"] + " / M01", same_number(metrics["gunluk_arac_enerji_ihtiyaci_kwh"], energy))
        check(item["charger_id"] + " / M02 kanıtlı ve pozitif", metrics["arac_wallbox_teorik_etkin_guc_kw"] is not None
              and metrics["arac_wallbox_teorik_etkin_guc_kw"] > 0)
        if energy is None:
            check(item["charger_id"] + " / eksik enerji korunuyor", metrics["teorik_gunluk_ihtiyac_karsilama_suresi_saat"] is None
                  and metrics["gunluk_ihtiyac_karsilama_orani"] is None)
        if user.get("butce_tl") is None:
            check(item["charger_id"] + " / opsiyonel bütçe korunuyor", metrics["fiyat_butce_orani"] is None)
    focus = next((i for i in all_items if i["charger_id"] == scenario.get("focus_charger_id")), None)
    expected_status = None
    expected_match = None
    if scenario.get("source_test_id"):
        test = tests[scenario["source_test_id"]]
        check("Teknik test referansı odak araç ve ürünle eşleşiyor", test["vehicle_id"] == scenario["vehicle_id"]
              and test["charger_id"] == scenario["focus_charger_id"])
        statuses = {"uygun": "DEGERLENDIR", "uygun_degil": "ELE", "dogrulama_gerekli": "DOGRULAMA_GEREKLI"}
        expected_status = statuses[test["beklenen_teknik_durum"]]
        expected_match = focus["hard_rule"]["status"] == expected_status
        check("Odak hard-rule sonucu teknik testle eşleşiyor", expected_match)
        if expected_status == "DEGERLENDIR":
            raw_power = test["beklenen_etkin_guc_kw"]
            expected_power = float(str(raw_power).replace(",", "."))
            check("Odak M02 teknik testle eşleşiyor", same_number(
                focus.get("metrics", {}).get("arac_wallbox_teorik_etkin_guc_kw"), expected_power))
        if expected_status == "ELE":
            check("Beklenen ELE ürünü eligible listesinde yok", focus not in candidates["eligible"])
    if scenario["scenario_id"] == "D4-020":
        # Genel uyarı metni statü etiketi değildir. HR06 sözlüğünün açık semantiği.
        check("D4-020 HR06 Bilinmiyor doğrulaması", focus["hard_rule"]["status"] == "DOGRULAMA_GEREKLI")
    if scenario["dataset_id"] == "D3":
        if scenario["candidate_pool_id"] == "POOL_EKSIK_VERI_3":
            check("HR01 eksik kayıtları normal değerlendirmeye almadı", len(candidates["insufficient_data"]) == len(all_items))
        if scenario["home_faz"] == "belirsiz":
            check("Belirsiz faz doğrulama gerektiriyor", not candidates["eligible"] and bool(candidates["needs_verification"]))
        if scenario["candidate_pool_id"] == "POOL_DLM_BILINMIYOR":
            check("DLM bilinmiyor uyarısı", all(any(w.startswith("DLM_DOGRULAMA") for w in i["warnings"]) for i in all_items))
        if scenario["candidate_pool_id"] == "POOL_FIYAT_BILINMIYOR":
            check("Fiyat bilinmiyor uyarısı", all(any(w.startswith("FIYAT_BILINMIYOR") for w in i["warnings"]) for i in all_items))
    return checks, energy, focus, expected_status, expected_match


def run_benchmark(root=ROOT):
    paths, vehicles, wallboxes, homes, scenarios, tests, pools = load_inputs(root)
    original = copy.deepcopy((vehicles, wallboxes, homes))
    rows = []
    traces = []
    errors = []
    check_count = 0
    passed_count = 0
    for scenario in scenarios:
        home, vehicle, user = scenario_inputs(scenario, homes, vehicles)
        selected = [wallboxes[c] for c in pools[scenario["candidate_pool_id"]]["charger_ids"]]
        candidates = recommend_candidates(home, vehicle, user, selected)
        checks, energy, focus, expected_status, expected_match = check_scenario(scenario, candidates, user, vehicle, tests)
        if sum(len(items) for items in candidates.values()) != len(selected):
            checks.append({"check": "Havuzdaki bütün ürünler değerlendirildi", "passed": False})
        failed = [c["check"] for c in checks if not c["passed"]]
        check_count += len(checks)
        passed_count += sum(c["passed"] for c in checks)
        errors.extend({"scenario_id": scenario["scenario_id"], "check": name} for name in failed)
        row = {"scenario_id": scenario["scenario_id"], "dataset_group": scenario["dataset_id"]}
        row.update({column: len(candidates[group]) for group, column in GROUPS.items()})
        row.update({"candidate_pool_id": scenario["candidate_pool_id"], "focus_charger_id": scenario.get("focus_charger_id"),
                    "focus_status": None if focus is None else focus["hard_rule"]["status"],
                    "expected_status": expected_status, "expected_match": expected_match,
                    "expected_behavior_text": scenario["beklenen_sistem_davranisi"],
                    "gunluk_arac_enerji_ihtiyaci_kwh": energy, "failed_checks": " | ".join(failed)})
        rows.append(row)
        traces.append({"scenario_id": scenario["scenario_id"], "dataset_id": scenario["dataset_id"],
                       "candidates": candidates, "checks": checks})
    if (vehicles, wallboxes, homes) != original:
        errors.append({"check": "Kaynak kayıtlar değiştirildi"})
    totals = {column: sum(row[column] for row in rows) for column in GROUPS.values()}
    groups = {group: {"scenario_count": sum(r["dataset_group"] == group for r in rows),
                      **{column: sum(r[column] for r in rows if r["dataset_group"] == group) for column in totals}}
              for group in ("D1", "D2", "D3", "D4")}
    summary = {"total_scenarios": len(rows), "total_alternatives": sum(totals.values()), "totals": totals,
               "dataset_groups": groups, "checks": {"total": check_count, "passed": passed_count, "failed": check_count - passed_count},
               "expected_status_comparisons": sum(r["expected_status"] is not None for r in rows),
               "expected_status_matches": sum(r["expected_match"] is True for r in rows),
               "source_records_unchanged": (vehicles, wallboxes, homes) == original,
               "errors": errors, "sources": {key: str(path.relative_to(root)) for key, path in paths.items()},
               "notes": ["Kullanıcı girdileri senaryo alanlarından okunur; bağımsız kullanıcı profil tablosu pakette yok.",
                         "D4-001–D4-019 kaynak teknik testle karşılaştırılır; D4-020 HR06 semantik kontrolüdür.",
                         "Genel uyarı metinleri otomatik statüye çevrilmez; DLM/bütçe/WLTP eksikliği teknik eleme değildir.",
                         "TC-20–TC-22, 85 senaryonun source_test_id referanslarında yoktur; ayrı test olarak çalıştırılmadı.",
                         "Güçler teorik araç–wallbox sınırıdır; kurulum onayı veya güvenli ev gücü değildir."]}
    output = root / "results"
    output.mkdir(exist_ok=True)
    with (output / "benchmark_results.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for filename, value in (("summary.json", summary), ("candidate_results.json", traces)):
        with (output / filename).open("w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
    print(f"Toplam senaryo: {len(rows)} / alternatif değerlendirmesi: {sum(totals.values())}")
    print("Grup  Senaryo  DEGERLENDIR  ELE  DOGRULAMA_GEREKLI  VERI_YETERSIZ")
    for group, counts in groups.items():
        print(f"{group:4} {counts['scenario_count']:7} {counts['eligible_count']:11} {counts['excluded_count']:4} "
              f"{counts['verification_count']:18} {counts['insufficient_data_count']:14}")
    print("Toplam:", totals)
    print(f"Kontroller: {passed_count}/{check_count}; beklenen statü: "
          f"{summary['expected_status_matches']}/{summary['expected_status_comparisons']}")
    for error in errors:
        print("HATA:", error)
    print("Not: D4-020 uyarı metni HR06 ile ayrıca kontrol edildi; statü etiketi olarak sayılmadı.")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Veri paketinin kök klasörü")
    args = parser.parse_args()
    try:
        result = run_benchmark(args.root.resolve())
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"NEED_INPUT / GİRDİ HATASI: {error}")
        raise SystemExit(1)
    raise SystemExit(1 if result["errors"] else 0)
