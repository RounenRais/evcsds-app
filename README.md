# Ev tipi AC wallbox karar destek motoru

Motor teknik kurallarla adayları ayırır ve uygun adaylarda M01–M06 metriklerini hesaplar. Ürün sıralaması veya kurulum güvenliği onayı üretmez.

## Klasörler

- `kds_engine/`: dört Python kaynak dosyası.
- `data/`: gerçek araç/wallbox kayıtları, ev profilleri, 85 senaryo ve teknik testler.
- `data/kaynaklar/`: geniş wallbox tablosu ve alan kaynakları.
- `docs/`: kural, metrik ve yöntem belgeleri; gelecekte kullanılabilecek MCDM şablonları.
- `results/`: benchmark CSV, özet ve adayların kural/metrik izleri.
- `reports/`: sunum için PDF raporu ve düzenlenebilir HTML kaynağı.

## Çalıştırma

Proje kök klasöründen, Python kuruluysa:

```powershell
python -B -m kds_engine.run_benchmark
```

Bu bilgisayarda kullanılan taşınabilir Python ile:

```powershell
& "$env:LOCALAPPDATA\Codex\kds-python-3.13.7\python.exe" -B -m kds_engine.run_benchmark
```

Haricî Python paketi gerektirmez. `-B` geçici `__pycache__` dosyalarını oluşturmaz.

## Veriler

- `ARAC_KDS_CEKIRDEK_100.json`: 100 gerçek araç kaydı.
- `WALLBOX_KDS_CEKIRDEK_30_V1_1.json`: 30 wallbox kaydı.
- `KDS_EV_PROFILLERI_V1.json`: 15 kontrollü ev profili.
- `KDS_BENCHMARK_D1_D4.json`: D1–D4 için 85 senaryo; kullanıcı girdileri bu kayıtlarda bulunur.
- `KDS_TEKNIK_ESLESME_TEST_VAKALARI.xlsx`: kaynak teknik test tablosu.
- `KDS_ADAY_HAVUZLARI_V1.json`: runner'ın kullandığı 10 özgün havuz.
- `KDS_ADAY_HAVUZLARI.json`: ayrıca istenen üç havuzun `V1_REBUILT` çıktısı.

Teslim paketindeki yanlış adlar ve uzantılar içeriklerine göre düzeltilmiştir. `docs/` altındaki özgün belgeler tarihsel paket referansları içerebilir. `ORIJINAL_PAKET_VERIFY_MANIFEST.txt`, ilk teslim paketinin hash kaydıdır; mevcut klasör yollarının manifesti değildir.

## Doğrulanan sonuç

85 senaryo, 2.153 alternatif değerlendirmesi; 842 DEGERLENDIR, 142 ELE, 1.160 DOGRULAMA_GEREKLI, 9 VERI_YETERSIZ. 2.683 otomatik kontrol geçti; açık beklenen statülü 19 D4 testi eşleşti. D4-020 ayrıca HR06 semantik kontrolünden geçti. Bu sonuçlar mevcut kontrollü deney paketine aittir.
