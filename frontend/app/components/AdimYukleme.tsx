"use client";

import { useState } from "react";
import { Dugme, Ok } from "./Cerceve";

function YuklemeKutusu({
  kimlik,
  baslik,
  aciklama,
  dosya,
  onSec,
  ikon,
}: {
  kimlik: string;
  baslik: string;
  aciklama: string;
  dosya: File | null;
  onSec: (d: File | null) => void;
  ikon: React.ReactNode;
}) {
  return (
    <section
      className={`flex-1 basis-[380px] min-w-0 bg-kart rounded-2xl p-8 sm:p-10 text-center border-[1.5px] border-dashed transition-colors ${
        dosya ? "border-uygun bg-uygun-acik/40" : "border-cizgi-koyu hover:border-vurgu"
      }`}
    >
      <div className="w-[52px] h-[52px] mx-auto mb-[18px] rounded-2xl bg-vurgu-acik grid place-items-center text-vurgu">
        {ikon}
      </div>
      <h2 className="m-0 mb-[7px] text-xl font-semibold tracking-tight">{baslik}</h2>
      <p className="m-0 mb-6 text-[15px] leading-relaxed text-murekkep-2">
        {dosya ? dosya.name : aciklama}
      </p>
      <label
        htmlFor={kimlik}
        className="inline-block px-6 min-h-[46px] leading-[46px] border border-cizgi-koyu rounded-[10px] bg-kart text-[15px] font-medium cursor-pointer hover:bg-[#faf9f7]"
      >
        {dosya ? "Değiştir" : "Fotoğraf seç"}
      </label>
      <input
        id={kimlik}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        className="sr-only"
        onChange={(e) => onSec(e.target.files?.[0] ?? null)}
      />
    </section>
  );
}

export default function AdimYukleme({
  onAnaliz,
  onElleGir,
  calisiyor,
}: {
  onAnaliz: (sayac: File, fatura: File) => void;
  onElleGir: () => void;
  calisiyor: boolean;
}) {
  const [sayac, setSayac] = useState<File | null>(null);
  const [fatura, setFatura] = useState<File | null>(null);

  return (
    <>
      <h1 className="m-0 mb-[18px] text-4xl sm:text-5xl leading-[1.08] font-semibold tracking-[-0.032em] max-w-[740px]">
        Evinize uygun şarj ünitesini bulalım
      </h1>
      <p className="m-0 mb-13 text-lg sm:text-[19px] leading-relaxed text-murekkep-2 max-w-[560px]">
        İki fotoğraf yeterli. Gerisini biz hesaplarız.
      </p>

      <div className="flex flex-wrap gap-6 mb-9 mt-10">
        <YuklemeKutusu
          kimlik="sayac-dosya"
          baslik="Elektrik sayacı"
          aciklama="Faz tipinizi okuruz"
          dosya={sayac}
          onSec={setSayac}
          ikon={
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <rect x="3" y="4" width="18" height="16" rx="2.5" />
              <rect x="6.5" y="8" width="11" height="5" rx="1" />
              <path d="M8 17h2M14 17h2" />
            </svg>
          }
        />
        <YuklemeKutusu
          kimlik="fatura-dosya"
          baslik="Elektrik faturası"
          aciklama="Sözleşme gücünüzü okuruz"
          dosya={fatura}
          onSec={setFatura}
          ikon={
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M5 3h14v18l-3-2-2 2-2-2-2 2-2-2-3 2Z" />
              <path d="M9 8h6M9 12h6M9 16h3" />
            </svg>
          }
        />
      </div>

      <div className="flex flex-wrap gap-5 items-center mb-10">
        <Dugme
          onClick={() => sayac && fatura && onAnaliz(sayac, fatura)}
          disabled={!sayac || !fatura || calisiyor}
        >
          {calisiyor ? "Analiz ediliyor…" : "Analizi başlat"}
          {!calisiyor && <Ok />}
        </Dugme>
        <button
          type="button"
          onClick={onElleGir}
          className="text-[15px] font-medium text-vurgu-koyu hover:underline"
        >
          Bilgileri elle gireceğim
        </button>
      </div>

      <p className="m-0 text-sm leading-relaxed text-murekkep-3 max-w-[620px]">
        Görseller analiz biter bitmez silinir. Faturadaki ad, adres ve tesisat
        numarası hiçbir yere kaydedilmez.
      </p>
    </>
  );
}
