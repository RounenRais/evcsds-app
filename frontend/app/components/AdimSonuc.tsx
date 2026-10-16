"use client";

import { useMemo, useState } from "react";
import {
  paraTl,
  sayi,
  yuzde,
  type Aday,
  type GrupAdi,
  type OneriSonucu,
} from "../lib/api";
import MarkaIsareti from "./MarkaIsareti";
import { Dugme } from "./Cerceve";

const GRUPLAR: { kimlik: GrupAdi; ad: string; renk: string; yazi: string }[] = [
  { kimlik: "uygun", ad: "Uygun", renk: "bg-uygun", yazi: "text-uygun-yazi" },
  { kimlik: "dogrulanmali", ad: "Doğrulanmalı", renk: "bg-uyari", yazi: "text-uyari-yazi" },
  { kimlik: "elenen", ad: "Elenen", renk: "bg-elenen", yazi: "text-elenen-yazi" },
  { kimlik: "veri_yetersiz", ad: "Veri yetersiz", renk: "bg-notr", yazi: "text-murekkep-2" },
];

const BOS_METIN: Record<GrupAdi, { baslik: string; aciklama: string }> = {
  uygun: {
    baslik: "Uygun ürün çıkmadı",
    aciklama:
      "Girdilerinizle hiçbir ürün bütün teknik kuralları geçemedi. «Doğrulanmalı» listesine bakın — oradaki ürünler eksik bilgi yüzünden bekliyor, uyumsuz oldukları için değil.",
  },
  dogrulanmali: {
    baslik: "Doğrulanacak ürün yok",
    aciklama: "Her ürün için yeterli bilgi vardı.",
  },
  elenen: {
    baslik: "Hiçbir ürün elenmedi",
    aciklama: "Eleme yalnızca kanıtlı bir uyumsuzlukta olur.",
  },
  veri_yetersiz: {
    baslik: "Katalog kaydı eksik ürün yok",
    aciklama: "Bütün kayıtlar değerlendirmeye uygundu.",
  },
};

function FiyatGrafigi({ adaylar, butce }: { adaylar: Aday[]; butce: number | null }) {
  const fiyatli = useMemo(
    () =>
      adaylar
        .filter((a) => a.urun.fiyat_tl !== null)
        .sort((a, b) => (a.urun.fiyat_tl ?? 0) - (b.urun.fiyat_tl ?? 0)),
    [adaylar]
  );

  if (fiyatli.length === 0) return null;

  const enYuksek = Math.max(...fiyatli.map((a) => a.urun.fiyat_tl ?? 0));
  const olcek = butce ? Math.max(enYuksek, butce) * 1.05 : enYuksek * 1.05;
  const fiyatsizSayisi = adaylar.length - fiyatli.length;

  return (
    <section className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_6px_20px_rgba(21,23,26,.045)] p-6 sm:p-8 mb-13">
      <h2 className="m-0 mb-2 text-2xl sm:text-[30px] leading-tight font-semibold tracking-[-0.025em]">
        Fiyatlar
      </h2>
      <p className="m-0 mb-7 text-base leading-relaxed text-murekkep-2">
        {adaylar.length} uygun üründen {fiyatli.length}’inde fiyat kaydı var.
        {butce !== null && " Dikey çizgi bütçenizi gösterir."}
      </p>

      <div className="relative">
        {butce !== null && butce > 0 && (
          <div
            className="absolute top-0 bottom-6 w-0.5 bg-elenen z-10"
            style={{ left: `calc(${(butce / olcek) * 100}% )` }}
            aria-hidden="true"
          />
        )}
        <div className="flex flex-col gap-3.5">
          {fiyatli.map((aday) => {
            const fiyat = aday.urun.fiyat_tl ?? 0;
            const asti = butce !== null && fiyat > butce;
            return (
              <div key={aday.charger_id} className="flex flex-wrap items-center gap-3">
                <div className="basis-[170px] grow-0 shrink-0 min-w-0 text-[14.5px] font-medium truncate sm:text-right">
                  {aday.urun.marka} {aday.urun.model}
                </div>
                <div className="flex-1 basis-[240px] min-w-0 flex items-center gap-3">
                  <div className="flex-1 min-w-0 h-[26px] bg-[#f4f3ef] rounded-[5px]">
                    <div
                      className={`h-full rounded-[5px] ${asti ? "bg-[#aec0ec]" : "bg-vurgu"}`}
                      style={{ width: `${(fiyat / olcek) * 100}%` }}
                    />
                  </div>
                  <span
                    className={`flex-none font-mono text-sm font-semibold w-[98px] text-right ${
                      asti ? "text-elenen-yazi" : ""
                    }`}
                  >
                    {paraTl(fiyat)}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
        {butce !== null && butce > 0 && (
          <p className="m-0 mt-2 font-mono text-xs font-semibold text-elenen-yazi">
            bütçeniz {paraTl(butce)}
          </p>
        )}
      </div>

      {fiyatsizSayisi > 0 && (
        <p className="m-0 mt-4 text-sm leading-relaxed text-murekkep-3">
          Diğer {fiyatsizSayisi} üründe fiyat kaydı yok. Teknik olarak uygunlar,
          yalnız karşılaştırmaya giremiyorlar.
        </p>
      )}
    </section>
  );
}

function AdayKarti({ aday }: { aday: Aday }) {
  const m = aday.metrikler;
  const kullanim = m?.nominal_kapasite_kullanim_orani ?? null;

  return (
    <article className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_5px_16px_rgba(21,23,26,.04)] px-5 sm:px-6 py-5 flex flex-wrap gap-5 items-center">
      <MarkaIsareti marka={aday.urun.marka} />

      <div className="flex-1 basis-[200px] min-w-0">
        <div className="text-[11.5px] font-semibold text-murekkep-3 uppercase tracking-[0.08em]">
          {aday.urun.marka}
        </div>
        <div className="text-[17px] font-semibold leading-tight tracking-tight mt-0.5">
          {aday.urun.model}
        </div>
        {aday.gerekceler.length > 0 && (
          <p className="mt-1.5 mb-0 text-sm leading-snug text-uyari-yazi">
            {aday.gerekceler[0]}
          </p>
        )}
      </div>

      {kullanim !== null && (
        <div className="basis-[190px] min-w-[160px] grow-0">
          <div className="flex items-baseline justify-between mb-1.5">
            <span className="text-[12.5px] text-murekkep-3">Kapasite kullanımı</span>
            <span className="font-mono text-sm font-semibold">{yuzde(kullanim)}</span>
          </div>
          <div className="h-2 bg-[#f4f3ef] rounded-full">
            <div
              className={`h-full rounded-full ${kullanim >= 1 ? "bg-uygun" : "bg-vurgu"}`}
              style={{ width: `${Math.min(100, kullanim * 100)}%` }}
            />
          </div>
        </div>
      )}

      <dl className="basis-[230px] min-w-[200px] grow-0 m-0 grid grid-cols-2 gap-3">
        <div>
          <dt className="text-[11.5px] text-murekkep-3 mb-0.5">Fiyat</dt>
          <dd className="m-0 font-mono text-[15px] font-semibold">
            {paraTl(aday.urun.fiyat_tl)}
          </dd>
        </div>
        <div>
          <dt className="text-[11.5px] text-murekkep-3 mb-0.5">Garanti</dt>
          <dd className="m-0 font-mono text-[15px] font-semibold">
            {aday.urun.garanti_yil ? `${aday.urun.garanti_yil} yıl` : "—"}
          </dd>
        </div>
      </dl>
    </article>
  );
}

export default function AdimSonuc({
  sonuc,
  onGeri,
}: {
  sonuc: OneriSonucu;
  onGeri: () => void;
}) {
  const [sekme, setSekme] = useState<GrupAdi>("uygun");
  const aktif = sonuc.gruplar[sekme];

  const ornek = sonuc.gruplar.uygun[0]?.metrikler ?? null;
  const arac = sonuc.girdi.arac;
  const guc = ornek?.arac_wallbox_teorik_etkin_guc_kw ?? null;

  return (
    <>
      <section className="bg-kart rounded-[20px] shadow-[0_1px_2px_rgba(21,23,26,.04),0_8px_28px_rgba(21,23,26,.05)] p-7 sm:p-11 mb-5">
        <div className="flex flex-wrap gap-10 items-center">
          <div className="flex-1 basis-[400px] min-w-0">
            <div className="text-xs font-semibold text-murekkep-3 uppercase tracking-[0.1em] mb-3.5">
              Sizin için en önemli sayı
            </div>
            <div className="flex items-baseline gap-2.5 mb-4">
              <span className="font-mono text-6xl sm:text-[76px] font-semibold leading-none tracking-[-0.04em]">
                {guc === null ? "—" : sayi(guc)}
              </span>
              <span className="text-2xl sm:text-[28px] font-medium text-murekkep-2">kW</span>
            </div>
            <p className="m-0 text-[17px] sm:text-lg leading-relaxed text-murekkep-2 max-w-[430px]">
              {arac.marka} {arac.model} aracınızın çekebileceği en yüksek AC gücü.{" "}
              <strong className="text-murekkep font-semibold">
                Daha güçlü bir ünite almanız bunu artırmaz.
              </strong>
            </p>
          </div>

          <dl className="basis-[300px] min-w-[250px] grow-0 m-0 sm:border-l border-[#f0eeea] sm:pl-9 flex flex-col gap-5">
            <div>
              <dt className="text-[13.5px] text-murekkep-3 mb-1">Günlük enerji ihtiyacınız</dt>
              <dd className="m-0 font-mono text-2xl font-semibold tracking-tight">
                {ornek?.gunluk_arac_enerji_ihtiyaci_kwh === null ||
                ornek?.gunluk_arac_enerji_ihtiyaci_kwh === undefined
                  ? "hesaplanamadı"
                  : sayi(ornek.gunluk_arac_enerji_ihtiyaci_kwh, "kWh")}
              </dd>
            </div>
            <div>
              <dt className="text-[13.5px] text-murekkep-3 mb-1">Şarj süresi</dt>
              <dd className="m-0 font-mono text-2xl font-semibold tracking-tight">
                {ornek?.teorik_gunluk_ihtiyac_karsilama_suresi_saat === null ||
                ornek?.teorik_gunluk_ihtiyac_karsilama_suresi_saat === undefined
                  ? "hesaplanamadı"
                  : sayi(ornek.teorik_gunluk_ihtiyac_karsilama_suresi_saat, "saat")}
              </dd>
            </div>
            <div>
              <dt className="text-[13.5px] text-murekkep-3 mb-1">İhtiyacınızın karşılanması</dt>
              <dd
                className={`m-0 font-mono text-2xl font-semibold tracking-tight ${
                  ornek?.gunluk_ihtiyac_karsilama_orani ? "text-uygun-yazi" : ""
                }`}
              >
                {ornek?.gunluk_ihtiyac_karsilama_orani === null ||
                ornek?.gunluk_ihtiyac_karsilama_orani === undefined
                  ? "hesaplanamadı"
                  : yuzde(ornek.gunluk_ihtiyac_karsilama_orani)}
              </dd>
            </div>
          </dl>
        </div>

        {arac.wltp_tuketim_kwh_100km === null && (
          <div className="mt-7 pt-6 border-t border-[#f0eeea] bg-uyari-acik -mx-7 sm:-mx-11 -mb-7 sm:-mb-11 px-7 sm:px-11 py-6 rounded-b-[20px]">
            <h3 className="m-0 mb-1.5 text-base font-semibold">
              Üç hesaplama yapılamadı
            </h3>
            <p className="m-0 text-[15px] leading-relaxed text-murekkep-2 max-w-[640px]">
              {arac.marka} {arac.model} için doğrulanmış tüketim değeri katalogda
              yok. Sistem tahmin üretmiyor — yanlış bir sayı, yanlış bir ünite
              seçimine yol açardı. Ürün ayrımı yine de eksiksiz yapıldı.
            </p>
          </div>
        )}
      </section>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-13">
        {GRUPLAR.map((g) => (
          <div
            key={g.kimlik}
            className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_5px_16px_rgba(21,23,26,.04)] px-6 py-5"
          >
            <div className="flex items-center gap-2 mb-2.5">
              <span className={`w-2.5 h-2.5 rounded-full flex-none ${g.renk}`} />
              <span className={`text-[13.5px] font-semibold ${g.yazi}`}>{g.ad}</span>
            </div>
            <div className="font-mono text-4xl font-semibold leading-none tracking-[-0.03em]">
              {sonuc.sayilar[g.kimlik]}
            </div>
          </div>
        ))}
      </div>

      <FiyatGrafigi adaylar={sonuc.gruplar.uygun} butce={sonuc.girdi.user.butce_tl} />

      <div role="tablist" aria-label="Sonuç grupları" className="flex flex-wrap gap-1.5 mb-5">
        {GRUPLAR.map((g) => {
          const secili = sekme === g.kimlik;
          return (
            <button
              key={g.kimlik}
              type="button"
              role="tab"
              aria-selected={secili}
              onClick={() => setSekme(g.kimlik)}
              className={`px-[18px] min-h-[46px] rounded-full border text-[14.5px] flex items-center gap-2.5 ${
                secili
                  ? "bg-murekkep border-murekkep text-white font-semibold"
                  : "bg-kart border-cizgi text-murekkep-2 font-medium hover:bg-[#faf9f7]"
              }`}
            >
              {g.ad}
              <span className="font-mono text-[13px] font-semibold opacity-70">
                {sonuc.sayilar[g.kimlik]}
              </span>
            </button>
          );
        })}
      </div>

      {aktif.length === 0 ? (
        <div className="bg-kart rounded-2xl shadow-[0_1px_2px_rgba(21,23,26,.04),0_6px_20px_rgba(21,23,26,.045)] px-8 py-14 text-center">
          <h3 className="m-0 mb-2.5 text-[22px] font-semibold tracking-tight">
            {BOS_METIN[sekme].baslik}
          </h3>
          <p className="m-0 mx-auto max-w-[460px] text-base leading-relaxed text-murekkep-2">
            {BOS_METIN[sekme].aciklama}
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {aktif.map((aday) => (
            <AdayKarti key={aday.charger_id} aday={aday} />
          ))}
        </div>
      )}

      <div className="mt-10 flex flex-wrap gap-3.5">
        <Dugme tur="ikincil" onClick={onGeri}>
          Girdileri değiştir
        </Dugme>
      </div>
    </>
  );
}
