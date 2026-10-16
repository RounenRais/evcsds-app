"use client";

import { useEffect, useState } from "react";
import { aracAra, sayi, type Arac, type Kullanim, type KurulumYeri } from "../lib/api";
import MarkaIsareti from "./MarkaIsareti";
import { Dugme, Ok, Unlem } from "./Cerceve";

function AracKarti({
  arac,
  secili,
  onSec,
}: {
  arac: Arac;
  secili: boolean;
  onSec: () => void;
}) {
  const wltpYok = arac.wltp_tuketim_kwh_100km === null;
  const ac = arac.ac_uc_faz_azami_guc_kw ?? arac.ac_tek_faz_azami_guc_kw;

  return (
    <button
      type="button"
      onClick={onSec}
      aria-pressed={secili}
      className={`text-left p-[22px] rounded-2xl bg-kart border-2 flex flex-col gap-4 transition-shadow ${
        secili
          ? "border-vurgu shadow-[0_1px_2px_rgba(42,91,215,.10),0_8px_24px_rgba(42,91,215,.12)]"
          : "border-transparent shadow-[0_1px_2px_rgba(21,23,26,.04),0_6px_18px_rgba(21,23,26,.045)]"
      }`}
    >
      <span className="flex items-center gap-[13px]">
        <MarkaIsareti marka={arac.marka} secili={secili} />
        <span className="min-w-0">
          <span className="block text-[11.5px] font-semibold text-murekkep-3 uppercase tracking-[0.08em]">
            {arac.marka}
          </span>
          <span className="block text-base font-semibold leading-tight tracking-tight mt-0.5">
            {arac.model}
          </span>
        </span>
      </span>

      <dl className="m-0 flex flex-wrap gap-x-6 gap-y-2.5">
        <div className="min-w-0">
          <dt className="text-[11.5px] text-murekkep-3 mb-0.5">AC azami</dt>
          <dd className="m-0 font-mono text-[17px] font-semibold whitespace-nowrap">
            {sayi(ac, "kW")}
          </dd>
        </div>
        <div className="min-w-0">
          <dt className="text-[11.5px] text-murekkep-3 mb-0.5">Tüketim</dt>
          <dd
            className={`m-0 font-mono text-[17px] font-semibold whitespace-nowrap ${
              wltpYok ? "text-uyari-yazi" : ""
            }`}
          >
            {wltpYok ? "veri yok" : sayi(arac.wltp_tuketim_kwh_100km)}
          </dd>
        </div>
      </dl>
    </button>
  );
}

const girdiSinifi =
  "w-full min-h-[52px] px-3.5 py-3 rounded-[10px] border-[1.5px] border-cizgi bg-kart font-mono text-[19px] font-medium text-murekkep";

export default function AdimArac({
  onDegerlendir,
  onGeri,
  calisiyor,
}: {
  onDegerlendir: (vehicleId: string, kullanim: Kullanim) => void;
  onGeri: () => void;
  calisiyor: boolean;
}) {
  const [sorgu, setSorgu] = useState("");
  const [araclar, setAraclar] = useState<Arac[]>([]);
  const [yukleniyor, setYukleniyor] = useState(true);
  const [aramaHatasi, setAramaHatasi] = useState<string | null>(null);
  const [secili, setSecili] = useState<Arac | null>(null);

  const [km, setKm] = useState("55");
  const [saat, setSaat] = useState("9");
  const [butce, setButce] = useState("");
  const [yer, setYer] = useState<KurulumYeri>("Dış mekan");

  // Yazma durduktan 250 ms sonra arama yapılır; her tuşta istek atılmaz.
  useEffect(() => {
    let iptal = false;
    const zaman = setTimeout(() => {
      setYukleniyor(true);
      aracAra(sorgu)
        .then((y) => {
          if (iptal) return;
          setAraclar(y.araclar);
          setAramaHatasi(null);
        })
        .catch((h: Error) => !iptal && setAramaHatasi(h.message))
        .finally(() => !iptal && setYukleniyor(false));
    }, 250);
    return () => {
      iptal = true;
      clearTimeout(zaman);
    };
  }, [sorgu]);

  const sayiyaCevir = (metin: string): number | null => {
    const temiz = metin.replace(",", ".").trim();
    if (temiz === "") return null;
    const deger = Number(temiz);
    return Number.isFinite(deger) ? deger : null;
  };

  return (
    <>
      <h1 className="m-0 mb-4 text-3xl sm:text-[42px] leading-[1.1] font-semibold tracking-[-0.03em]">
        Aracınız hangisi?
      </h1>
      <p className="m-0 mb-8 text-lg leading-relaxed text-murekkep-2 max-w-[560px]">
        Katalogda 100 elektrikli araç var.
      </p>

      <label htmlFor="arac-ara" className="sr-only">
        Araç ara
      </label>
      <input
        id="arac-ara"
        type="search"
        value={sorgu}
        onChange={(e) => setSorgu(e.target.value)}
        placeholder="Marka veya model ara"
        className="w-full min-h-[54px] px-[18px] py-3.5 rounded-xl border border-cizgi-koyu bg-kart text-base text-murekkep"
      />

      <p className="mt-3 mb-5 text-[13.5px] text-murekkep-3" aria-live="polite">
        {yukleniyor
          ? "Aranıyor…"
          : sorgu.trim()
            ? `${araclar.length} araç bulundu`
            : `${araclar.length} araç gösteriliyor`}
      </p>

      {aramaHatasi && (
        <div role="alert" className="flex gap-3 bg-elenen-acik rounded-xl px-5 py-4 mb-6">
          <span className="text-elenen-yazi flex-none mt-0.5">
            <Unlem boyut={18} />
          </span>
          <p className="m-0 text-[14.5px] text-murekkep-2">{aramaHatasi}</p>
        </div>
      )}

      {!yukleniyor && !aramaHatasi && araclar.length === 0 && (
        <div className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_5px_16px_rgba(21,23,26,.04)] px-8 py-12 text-center mb-13">
          <h3 className="m-0 mb-2 text-xl font-semibold tracking-tight">Eşleşen araç yok</h3>
          <p className="m-0 mx-auto mb-5 max-w-[380px] text-[15.5px] leading-relaxed text-murekkep-2">
            Yazımı kontrol edin.
          </p>
          <Dugme tur="ikincil" onClick={() => setSorgu("")}>
            Aramayı temizle
          </Dugme>
        </div>
      )}

      {araclar.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-13">
          {araclar.map((arac) => (
            <AracKarti
              key={arac.vehicle_id}
              arac={arac}
              secili={secili?.vehicle_id === arac.vehicle_id}
              onSec={() => setSecili(arac)}
            />
          ))}
        </div>
      )}

      <h2 className="m-0 mt-12 mb-4 text-2xl sm:text-[32px] leading-tight font-semibold tracking-[-0.025em]">
        Günlük kullanımınız
      </h2>
      <p className="m-0 mb-7 text-[17px] leading-relaxed text-murekkep-2 max-w-[560px]">
        Tahmini değerler yeterli.
      </p>

      <div className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_6px_20px_rgba(21,23,26,.045)] p-6 sm:p-8 grid grid-cols-1 md:grid-cols-2 gap-7 md:gap-x-9 mb-10">
        <div>
          <label htmlFor="km" className="block text-base font-semibold tracking-tight mb-2.5">
            Günde kaç kilometre?
          </label>
          <div className="flex items-center gap-3">
            <input id="km" inputMode="decimal" value={km} onChange={(e) => setKm(e.target.value)} className={girdiSinifi} />
            <span className="text-[15px] font-medium text-murekkep-2">km</span>
          </div>
        </div>

        <div>
          <label htmlFor="saat" className="block text-base font-semibold tracking-tight mb-2.5">
            Evde kaç saat park halinde?
          </label>
          <div className="flex items-center gap-3">
            <input id="saat" inputMode="decimal" value={saat} onChange={(e) => setSaat(e.target.value)} className={girdiSinifi} />
            <span className="text-[15px] font-medium text-murekkep-2">saat</span>
          </div>
        </div>

        <div>
          <label htmlFor="butce" className="block text-base font-semibold tracking-tight mb-1">
            Bütçeniz
          </label>
          <p className="m-0 mb-2.5 text-[13.5px] text-murekkep-3">
            Opsiyonel — boş bırakmak hiçbir ürünü elemez
          </p>
          <div className="flex items-center gap-3">
            <input id="butce" inputMode="numeric" value={butce} placeholder="40000" onChange={(e) => setButce(e.target.value)} className={girdiSinifi} />
            <span className="text-[15px] font-medium text-murekkep-2">TL</span>
          </div>
        </div>

        <fieldset className="border-0 p-0 m-0">
          <legend className="text-base font-semibold tracking-tight mb-2.5 p-0">
            Nereye monte edilecek?
          </legend>
          <div className="flex gap-3">
            {(["İç mekan", "Dış mekan"] as KurulumYeri[]).map((secenek) => (
              <label
                key={secenek}
                className={`flex-1 flex items-center gap-2.5 min-h-[52px] px-4 py-3 rounded-[10px] border-2 cursor-pointer text-base ${
                  yer === secenek
                    ? "border-vurgu bg-vurgu-acik font-semibold"
                    : "border-cizgi"
                }`}
              >
                <input
                  type="radio"
                  name="kurulum-yeri"
                  value={secenek}
                  checked={yer === secenek}
                  onChange={() => setYer(secenek)}
                  className="w-[18px] h-[18px] accent-[#2a5bd7]"
                />
                {secenek === "İç mekan" ? "İç mekân" : "Dış mekân"}
              </label>
            ))}
          </div>
        </fieldset>
      </div>

      <div className="flex flex-wrap gap-3.5 items-center">
        <Dugme
          onClick={() =>
            secili &&
            onDegerlendir(secili.vehicle_id, {
              gunluk_ortalama_km: sayiyaCevir(km),
              evde_sarj_icin_uygun_sure_saat: sayiyaCevir(saat),
              butce_tl: sayiyaCevir(butce),
              kurulum_yeri: yer,
            })
          }
          disabled={!secili || calisiyor}
        >
          {calisiyor ? "Değerlendiriliyor…" : "30 ürünü değerlendir"}
          {!calisiyor && <Ok />}
        </Dugme>
        <Dugme tur="ikincil" onClick={onGeri}>
          Geri
        </Dugme>
        {!secili && (
          <span className="text-sm text-murekkep-3">Önce bir araç seçin.</span>
        )}
      </div>
    </>
  );
}
