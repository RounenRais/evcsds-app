"use client";
import { useState } from "react";

export default function Home() {
  const [dosya, setDosya] = useState<File | null>(null);
  const [sonuc, setSonuc] = useState<any>(null);
  const [yukleniyor, setYukleniyor] = useState(false);
  const [onizleme, setOnizleme] = useState<string | null>(null);

  // Dosya seçilince
  const dosyaSec = (e: React.ChangeEvent<HTMLInputElement>) => {
    const secilen = e.target.files?.[0];
    if (!secilen) return;
    setDosya(secilen);
    setSonuc(null);

    // Önizleme göster
    const reader = new FileReader();
    reader.onload = () => setOnizleme(reader.result as string);
    reader.readAsDataURL(secilen);
  };

  // Analiz et butonuna basınca
  const analizeEt = async () => {
    if (!dosya) return;
    setYukleniyor(true);
    setSonuc(null);

    const form = new FormData();
    form.append("file", dosya);

    try {
      const res = await fetch("http://localhost:8000/fatura-analiz", {
        method: "POST",
        body: form,
      });
      const veri = await res.json();
      setSonuc(veri);
    } catch (err) {
      setSonuc({ basarili: false, mesaj: "Sunucuya bağlanılamadı!" });
    } finally {
      setYukleniyor(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 flex items-center justify-center p-8">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-xl">
        
        {/* Başlık */}
        <h1 className="text-2xl font-bold text-gray-800 mb-2">
          EV Şarj İstasyonu Karar Destek
        </h1>
        <p className="text-gray-500 mb-6">
          Elektrik faturanızı yükleyin, altyapınızı analiz edelim.
        </p>

        {/* Dosya Yükleme */}
        <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center mb-4">
          <input
            type="file"
            accept="image/*"
            onChange={dosyaSec}
            className="hidden"
            id="dosya-input"
          />
          <label htmlFor="dosya-input" className="cursor-pointer">
            <div className="text-4xl mb-2">📄</div>
            <p className="text-gray-600">
              Fatura fotoğrafını seç veya sürükle
            </p>
            <p className="text-gray-400 text-sm mt-1">
              JPG, PNG desteklenir
            </p>
          </label>
        </div>

        {/* Önizleme */}
        {onizleme && (
          <div className="mb-4">
            <img
              src={onizleme}
              alt="Fatura önizleme"
              className="w-full max-h-64 object-contain rounded-lg border"
            />
          </div>
        )}

        {/* Analiz Butonu */}
        <button
          onClick={analizeEt}
          disabled={!dosya || yukleniyor}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 
                     text-white font-semibold py-3 rounded-xl transition-colors"
        >
          {yukleniyor ? "Analiz ediliyor..." : "Analiz Et"}
        </button>

        {/* Sonuç */}
        {sonuc && (
          <div className={`mt-6 p-4 rounded-xl ${
            sonuc.basarili ? "bg-green-50 border border-green-200" : "bg-yellow-50 border border-yellow-200"
          }`}>
            {sonuc.basarili ? (
              <div>
                <p className="text-green-700 font-semibold text-lg">
                  ✅ Sözleşme Gücü: {sonuc.sozlesme_gucu} kW
                </p>
                <p className="text-green-600 text-sm mt-1">{sonuc.mesaj}</p>
              </div>
            ) : (
              <div>
                <p className="text-yellow-700 font-semibold">
                  ⚠️ Otomatik tespit edilemedi
                </p>
                <p className="text-yellow-600 text-sm mt-1">{sonuc.mesaj}</p>
                
                {/* Manuel giriş */}
                <div className="mt-3">
                  <label className="text-yellow-700 text-sm font-medium">
                    Sözleşme gücünü manuel girin (kW):
                  </label>
                  <input
                    type="number"
                    placeholder="örn: 7.5"
                    className="mt-1 w-full border border-yellow-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </main>
  );
}