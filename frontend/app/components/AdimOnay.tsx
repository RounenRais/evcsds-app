"use client";

import { useState } from "react";
import type { EvGirdisi, Faz } from "../lib/api";
import { Dugme, Ok, Tik, Unlem } from "./Cerceve";

/** Alanın otomatik okunup okunmadığını gösteren rozet. */
function Rozet({ okundu }: { okundu: boolean }) {
  return (
    <span
      className={`flex-none inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[13px] font-semibold whitespace-nowrap ${
        okundu
          ? "bg-uygun-acik text-uygun-yazi"
          : "bg-uyari-acik text-uyari-yazi"
      }`}
    >
      {okundu ? <Tik /> : <Unlem />}
      {okundu ? "Okundu" : "Okunamadı"}
    </span>
  );
}

function Satir({
  kimlik,
  ad,
  aciklama,
  okundu,
  children,
}: {
  kimlik: string;
  ad: string;
  aciklama: string;
  okundu: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="px-6 sm:px-8 py-6 border-b border-[#f0eeea] last:border-b-0 flex flex-wrap gap-5 items-center">
      <div className="flex-1 basis-[240px] min-w-0">
        <label htmlFor={kimlik} className="block text-[17px] font-semibold tracking-tight mb-[3px]">
          {ad}
        </label>
        <p className="m-0 text-sm leading-snug text-murekkep-3">{aciklama}</p>
      </div>
      <Rozet okundu={okundu} />
      <div className="basis-[240px] min-w-[200px] grow-0 shrink">{children}</div>
    </div>
  );
}

const girdiSinifi = (okundu: boolean) =>
  `w-full min-h-[50px] px-3.5 py-3 rounded-[10px] bg-kart font-mono text-[17px] font-medium text-murekkep border-[1.5px] ${
    okundu ? "border-cizgi" : "border-[#d9b868]"
  }`;

export default function AdimOnay({
  baslangic,
  otomatik,
  onOnay,
  onGeri,
}: {
  baslangic: EvGirdisi;
  /** Hangi alanlar görsellerden okunabildi. Elle girişte hepsi false olur. */
  otomatik: Record<keyof EvGirdisi, boolean>;
  onOnay: (ev: EvGirdisi) => void;
  onGeri: () => void;
}) {
  const [ev, setEv] = useState<EvGirdisi>(baslangic);

  const sayiyaCevir = (metin: string): number | null => {
    const temiz = metin.replace(/\./g, "").replace(",", ".").trim();
    if (temiz === "") return null;
    const deger = Number(temiz);
    return Number.isFinite(deger) ? deger : null;
  };

  const metin = (deger: number | null) =>
    deger === null ? "" : String(deger).replace(".", ",");

  return (
    <>
      <h1 className="m-0 mb-4 text-3xl sm:text-[42px] leading-[1.1] font-semibold tracking-[-0.03em]">
        Okuduklarımızı kontrol edin
      </h1>
      <p className="m-0 mb-11 text-lg leading-relaxed text-murekkep-2 max-w-[580px]">
        Hepsi birer öneri. Yanlış gördüğünüzü değiştirin.
      </p>

      <div className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_6px_20px_rgba(21,23,26,.045)] overflow-hidden mb-10">
        <Satir kimlik="faz" ad="Şebeke fazı" aciklama="Şarj hızınızın üst sınırı" okundu={otomatik.faz}>
          <select
            id="faz"
            value={ev.faz}
            onChange={(e) => setEv({ ...ev, faz: e.target.value as Faz })}
            className={`${girdiSinifi(otomatik.faz)} font-sans`}
          >
            <option value="trifaz">Trifaz</option>
            <option value="monofaz">Monofaz</option>
            <option value="belirsiz">Bilmiyorum</option>
          </select>
        </Satir>

        <Satir kimlik="guc" ad="Sözleşme gücü" aciklama="Faturadaki anlaşma gücü (kW)" okundu={otomatik.sozlesme_gucu_kw}>
          <input
            id="guc"
            inputMode="decimal"
            placeholder="örn. 9"
            value={metin(ev.sozlesme_gucu_kw)}
            onChange={(e) => setEv({ ...ev, sozlesme_gucu_kw: sayiyaCevir(e.target.value) })}
            className={girdiSinifi(otomatik.sozlesme_gucu_kw)}
          />
        </Satir>

        <Satir kimlik="donem" ad="Dönem tüketimi" aciklama="Son faturanın toplamı (kWh)" okundu={otomatik.donem_tuketimi_kwh}>
          <input
            id="donem"
            inputMode="decimal"
            placeholder="örn. 340"
            value={metin(ev.donem_tuketimi_kwh)}
            onChange={(e) => setEv({ ...ev, donem_tuketimi_kwh: sayiyaCevir(e.target.value) })}
            className={girdiSinifi(otomatik.donem_tuketimi_kwh)}
          />
        </Satir>

        <Satir kimlik="gunluk" ad="Günlük ortalama" aciklama="Günlük ortalama tüketim (kWh)" okundu={otomatik.gunluk_ortalama_kwh}>
          <input
            id="gunluk"
            inputMode="decimal"
            placeholder="örn. 11,3"
            value={metin(ev.gunluk_ortalama_kwh)}
            onChange={(e) => setEv({ ...ev, gunluk_ortalama_kwh: sayiyaCevir(e.target.value) })}
            className={girdiSinifi(otomatik.gunluk_ortalama_kwh)}
          />
        </Satir>

        <Satir kimlik="tarife" ad="Tarife" aciklama="Mesken veya ticarethane" okundu={otomatik.tarife}>
          <input
            id="tarife"
            value={ev.tarife ?? ""}
            placeholder="Elle girin"
            onChange={(e) => setEv({ ...ev, tarife: e.target.value || null })}
            className={`${girdiSinifi(otomatik.tarife)} font-sans text-[15px]`}
          />
        </Satir>

        <div className="px-6 sm:px-8 py-5 bg-uyari-acik flex gap-3 items-start">
          <span className="text-uyari-yazi flex-none mt-0.5">
            <Unlem boyut={18} />
          </span>
          <p className="m-0 text-[14.5px] leading-relaxed text-murekkep-2">
            Tarife ve dönem tüketimi zorunlu değil. Boş bırakırsanız sistem
            onlarsız devam eder. Faz bilinmiyorsa hiçbir ürün «uygun»
            sayılmaz, hepsi «doğrulanmalı» olur.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-3.5 items-center">
        <Dugme onClick={() => onOnay(ev)}>
          Onaylıyorum
          <Ok />
        </Dugme>
        <Dugme tur="ikincil" onClick={onGeri}>
          Geri
        </Dugme>
      </div>
    </>
  );
}
