import unittest

from bill_field_extractor import fatura_alanlarini_cikar


def ocr(text, x1, y1, x2, y2, score=0.98):
    return {
        "text": text,
        "score": score,
        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
    }


class FaturaAlanCikarmaTesti(unittest.TestCase):
    def test_enerjisa_birlesik_guc_satiri(self):
        metinler = [
            ocr("ENERJISA", 10, 10, 120, 35),
            ocr("Çarpan/Demand/Anl. Gücü", 10, 100, 270, 130),
            ocr("1,000/-/3,000", 300, 100, 460, 130),
            ocr("Dönem Tüketimi", 10, 200, 190, 230),
            ocr("246,186 kWh", 300, 200, 440, 230),
            ocr(
                "Tüketici Grubu: Mesken Tek Zamanlı (Alçak Gerilim)",
                10,
                300,
                600,
                330,
            ),
        ]
        sonuc = fatura_alanlarini_cikar(metinler, 1000, 1400)
        self.assertEqual(sonuc["ozet"]["sozlesme_gucu_kw"], 3.0)
        self.assertEqual(sonuc["ozet"]["carpan"], 1.0)
        self.assertIsNone(sonuc["ozet"]["demand_kw"])
        self.assertEqual(sonuc["ozet"]["donem_tuketimi_kwh"], 246.186)
        self.assertEqual(
            sonuc["ozet"]["tarife"], "mesken_tek_zamanli_alcak_gerilim"
        )
        self.assertFalse(sonuc["manuel_giris_gerekli"])

    def test_ayri_yazilmis_sozlesme_gucu(self):
        metinler = [
            ocr("Sözleşme Gücü", 10, 100, 190, 130),
            ocr("5,00 kW", 230, 100, 330, 130),
            ocr("Toplam Tüketim", 10, 200, 190, 230),
            ocr("185,20 kWh", 230, 200, 360, 230),
            ocr("Abone Grubu: Mesken Çok Zamanlı", 10, 300, 450, 330),
        ]
        sonuc = fatura_alanlarini_cikar(metinler, 1000, 1400)
        self.assertEqual(sonuc["ozet"]["sozlesme_gucu_kw"], 5.0)
        self.assertEqual(sonuc["ozet"]["donem_tuketimi_kwh"], 185.2)
        self.assertEqual(sonuc["ozet"]["tarife"], "mesken_cok_zamanli")

    def test_sonraki_okuma_donemini_fatura_donemi_sanmaz(self):
        metinler = [
            ocr("Sonraki Okuma Dönemi", 10, 100, 240, 130),
            ocr("05.2026", 300, 100, 390, 130),
            ocr("Toplam", 10, 200, 100, 230),
            ocr("2.982,186 kWh", 230, 200, 390, 230),
        ]
        sonuc = fatura_alanlarini_cikar(metinler, 1000, 1400)
        self.assertNotIn("fatura_donemi", sonuc["ozet"])
        self.assertNotIn("donem_tuketimi_kwh", sonuc["ozet"])
        self.assertTrue(sonuc["manuel_giris_gerekli"])

    def test_endeks_farkini_okuma_gunuyle_karistirmaz(self):
        metinler = [
            ocr("Okuma (Gün)", 144, 351, 542, 456),
            ocr("30", 2092, 378, 2177, 456),
            ocr("Tek Zaman (Endeks)", 144, 438, 752, 549),
            ocr("246,186", 1930, 461, 2176, 546),
        ]
        sonuc = fatura_alanlarini_cikar(metinler, 2400, 1100)
        self.assertEqual(sonuc["ozet"]["donem_tuketimi_kwh"], 246.186)

    def test_fatura_ortalamasini_yillik_ortalamaya_tercih_eder(self):
        metinler = [
            ocr("Fatura Ort. Tüketim", 700, 100, 1000, 180),
            ocr("20.04.202", 300, 220, 550, 290),
            ocr("8,206", 780, 220, 930, 290),
            ocr("Günlük Ortalama", 700, 700, 1000, 780),
            ocr("7,706 (kWh)", 780, 820, 1000, 890),
        ]
        sonuc = fatura_alanlarini_cikar(metinler, 1400, 1200)
        self.assertEqual(sonuc["ozet"]["gunluk_ortalama_kwh"], 8.206)


if __name__ == "__main__":
    unittest.main()
