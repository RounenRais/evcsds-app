"""Görsel analiz çıktısının karar motoruna sorunsuz girdiğini doğrular.

Bu dosya birleştirmenin asıl sözleşmesini test eder: `vision.home_input`
ne üretiyorsa `recommend` onu motora geçirebilmeli. Görsel katmanın ağır
bağımlılıkları (torch, paddleocr) gerekmez — `home_input` saf Python'dur.
"""

import unittest

import catalog
import recommend
from vision.home_input import kds_ev_girdisi_olustur


IONIQ = "EU_EVDB_2236_IONIQ_5_84_KWH_RWD_MY24"
TOGG = "EU_EVDB_3302_T10X_LONG_RANGE_RWD"

KULLANIM = {
    "gunluk_ortalama_km": 55.0,
    "evde_sarj_icin_uygun_sure_saat": 9.0,
    "butce_tl": 40000.0,
    "kurulum_yeri": "Dış mekan",
}


def sayac_sonucu(faz="trifaz"):
    return {"sayac_bulundu": True, "faz": faz}


def fatura_sonucu(guven=0.95):
    return {
        "fatura_bulundu": True,
        "tespit_yontemi": "yolo",
        "fatura_bilgileri": {
            "manuel_giris_alanlari": [],
            "alanlar": {
                "sozlesme_gucu_kw": {"deger": 9.0, "guven": guven},
                "donem_tuketimi_kwh": {"deger": 340.0, "guven": guven},
                "gunluk_ortalama_kwh": {"deger": 11.3, "guven": guven},
                "tarife": {"deger": "mesken_tek_zamanli_alcak_gerilim", "guven": guven},
            },
        },
    }


class KatalogTesti(unittest.TestCase):
    def test_katalog_beklenen_sayida_kayit_tutuyor(self):
        self.assertEqual(len(catalog.araclar()), 100)
        self.assertEqual(len(catalog.wallboxlar()), 30)

    def test_arama_noktali_ve_noktasiz_i_ayirmiyor(self):
        for yazim in ("IONIQ", "ioniq", "ıonıq", "İONİQ"):
            with self.subTest(yazim=yazim):
                self.assertTrue(catalog.arac_listesi(yazim))

    def test_arama_noktalamayi_yok_sayiyor(self):
        self.assertEqual(
            [a["vehicle_id"] for a in catalog.arac_listesi("id3")],
            [a["vehicle_id"] for a in catalog.arac_listesi("ID.3")],
        )

    def test_eslesmeyen_sorgu_bos_doner(self):
        self.assertEqual(catalog.arac_listesi("boyle-bir-arac-yok"), [])


class GorseldenMotoraTesti(unittest.TestCase):
    def test_home_input_ciktisi_motora_dogrudan_giriyor(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())

        # Görsel katman hiçbir değeri kendiliğinden onaylı saymaz.
        self.assertFalse(ev["kdsye_dogrudan_aktarilabilir"])
        self.assertEqual(ev["durum"], "kullanici_onayi_gerekli")

        sonuc = recommend.oneri_uret(ev["home"], IONIQ, KULLANIM, kullanici_onayladi=True)
        self.assertEqual(sonuc["toplam_degerlendirilen"], 30)
        self.assertEqual(sum(sonuc["sayilar"].values()), 30)
        self.assertTrue(sonuc["gruplar"]["uygun"])

    def test_onay_olmadan_oneri_uretilmiyor(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())
        with self.assertRaises(recommend.OneriGirdiHatasi):
            recommend.oneri_uret(ev["home"], IONIQ, KULLANIM, kullanici_onayladi=False)

    def test_belirsiz_faz_hicbir_urunu_uygun_saymiyor(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(faz=None), fatura_sonucu())
        self.assertEqual(ev["home"]["faz"], "belirsiz")

        sonuc = recommend.oneri_uret(ev["home"], IONIQ, KULLANIM, kullanici_onayladi=True)
        self.assertEqual(sonuc["sayilar"]["uygun"], 0)
        self.assertGreater(sonuc["sayilar"]["dogrulanmali"], 0)

    def test_dusuk_guvenli_fatura_alani_tasinmiyor(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu(guven=0.4))
        self.assertIsNone(ev["home"]["sozlesme_gucu_kw"])
        self.assertEqual(ev["durum"], "manuel_dogrulama_gerekli")


class MetrikDavranisiTesti(unittest.TestCase):
    def _metrikler(self, vehicle_id):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())
        sonuc = recommend.oneri_uret(ev["home"], vehicle_id, KULLANIM, kullanici_onayladi=True)
        return sonuc["gruplar"]["uygun"][0]["metrikler"]

    def test_wltp_bilinen_aracta_tum_metrikler_hesaplaniyor(self):
        metrikler = self._metrikler(IONIQ)
        for alan in (
            "gunluk_arac_enerji_ihtiyaci_kwh",
            "arac_wallbox_teorik_etkin_guc_kw",
            "teorik_gunluk_ihtiyac_karsilama_suresi_saat",
            "gunluk_ihtiyac_karsilama_orani",
        ):
            with self.subTest(alan=alan):
                self.assertIsNotNone(metrikler[alan])

    def test_wltp_eksik_aracta_tahmin_uretilmiyor(self):
        metrikler = self._metrikler(TOGG)
        # Enerjiye bağlı metrikler boş kalır...
        self.assertIsNone(metrikler["gunluk_arac_enerji_ihtiyaci_kwh"])
        self.assertIsNone(metrikler["teorik_gunluk_ihtiyac_karsilama_suresi_saat"])
        self.assertIsNone(metrikler["gunluk_ihtiyac_karsilama_orani"])
        # ...ama faz yolundan gelen güç yine de bulunur.
        self.assertIsNotNone(metrikler["arac_wallbox_teorik_etkin_guc_kw"])

    def test_butce_girilmezse_hicbir_urun_elenmiyor(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())
        butcesiz = {**KULLANIM, "butce_tl": None}
        ile = recommend.oneri_uret(ev["home"], IONIQ, KULLANIM, kullanici_onayladi=True)
        siz = recommend.oneri_uret(ev["home"], IONIQ, butcesiz, kullanici_onayladi=True)
        self.assertEqual(ile["sayilar"], siz["sayilar"])
        self.assertIsNone(siz["gruplar"]["uygun"][0]["metrikler"]["fiyat_butce_orani"])


class GirdiDogrulamaTesti(unittest.TestCase):
    def _ev(self):
        return kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())["home"]

    def test_gecersiz_faz_reddediliyor(self):
        with self.assertRaises(recommend.OneriGirdiHatasi):
            recommend.oneri_uret({"faz": "ucfaz"}, IONIQ, KULLANIM, kullanici_onayladi=True)

    def test_gecersiz_kurulum_yeri_reddediliyor(self):
        with self.assertRaises(recommend.OneriGirdiHatasi):
            recommend.oneri_uret(
                self._ev(), IONIQ, {**KULLANIM, "kurulum_yeri": "bahçe"}, kullanici_onayladi=True
            )

    def test_katalogda_olmayan_arac_reddediliyor(self):
        with self.assertRaises(recommend.OneriGirdiHatasi):
            recommend.oneri_uret(self._ev(), "YOK_123", KULLANIM, kullanici_onayladi=True)


class CiktiSozlesmesiTesti(unittest.TestCase):
    def test_her_urun_tam_olarak_bir_grupta(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())
        sonuc = recommend.oneri_uret(ev["home"], IONIQ, KULLANIM, kullanici_onayladi=True)
        kimlikler = [
            aday["charger_id"]
            for grup in sonuc["gruplar"].values()
            for aday in grup
        ]
        self.assertEqual(len(kimlikler), 30)
        self.assertEqual(len(set(kimlikler)), 30)

    def test_kurulum_onayi_uyarisi_her_yanitta_var(self):
        ev = kds_ev_girdisi_olustur(sayac_sonucu(), fatura_sonucu())
        sonuc = recommend.oneri_uret(ev["home"], IONIQ, KULLANIM, kullanici_onayladi=True)
        self.assertIn("kurulum onayı vermez", sonuc["uyari"])
        self.assertTrue(sonuc["siralama_yapilmadi"])


if __name__ == "__main__":
    unittest.main()
