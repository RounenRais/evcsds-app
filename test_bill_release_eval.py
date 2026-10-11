import unittest
from pathlib import Path

from bill_release_eval import alan_sonucu, kullanilabilir_aday, manifesti_oku


class FaturaYayinDegerlendirmeTesti(unittest.TestCase):
    def test_bos_sablon_gecerli_ama_dogruluk_sayilmaz(self):
        satirlar = manifesti_oku(
            Path("planning/FATURA_SAHA_DOGRULAMA_SABLONU.csv")
        )
        self.assertEqual(len(satirlar), 12)
        self.assertIsNone(alan_sonucu("sozlesme_gucu_kw", "dogrulanmadi", "", 6.408))

    def test_yanlis_dolu_ile_eksik_deger_ayri_sayilir(self):
        self.assertEqual(
            alan_sonucu("sozlesme_gucu_kw", "dogrulandi", "6.408", 24.0),
            "yanlis_dolu",
        )
        self.assertEqual(
            alan_sonucu("sozlesme_gucu_kw", "dogrulandi", "6.408", None),
            "kacirildi",
        )
        self.assertEqual(
            alan_sonucu("sozlesme_gucu_kw", "dogrulandi", "6.408", 6.408),
            "dogru_dolu",
        )

    def test_manuel_alan_ve_dusuk_guven_dogruluk_sanilmaz(self):
        analiz = {
            "fatura_bulundu": True,
            "fatura_bilgileri": {
                "alanlar": {"sozlesme_gucu_kw": {"deger": 6.408, "guven": 0.95}},
                "manuel_giris_alanlari": ["sozlesme_gucu_kw"],
            },
        }
        self.assertIsNone(kullanilabilir_aday(analiz, "sozlesme_gucu_kw"))
        analiz["fatura_bilgileri"]["manuel_giris_alanlari"] = []
        analiz["fatura_bilgileri"]["alanlar"]["sozlesme_gucu_kw"]["guven"] = 0.4
        self.assertIsNone(kullanilabilir_aday(analiz, "sozlesme_gucu_kw"))


if __name__ == "__main__":
    unittest.main()
