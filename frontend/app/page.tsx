"use client";

import { useState } from "react";
import {
  evAnaliziIste,
  oneriIste,
  type EvGirdisi,
  type Kullanim,
  type OneriSonucu,
} from "./lib/api";
import { Altbilgi, Baslik, Govde, Hata } from "./components/Cerceve";
import AdimYukleme from "./components/AdimYukleme";
import AdimOnay from "./components/AdimOnay";
import AdimArac from "./components/AdimArac";
import AdimSonuc from "./components/AdimSonuc";

type Adim = 0 | 1 | 2 | 3;

const BOS_EV: EvGirdisi = {
  faz: "belirsiz",
  sozlesme_gucu_kw: null,
  donem_tuketimi_kwh: null,
  gunluk_ortalama_kwh: null,
  tarife: null,
};

const HICBIRI: Record<keyof EvGirdisi, boolean> = {
  faz: false,
  sozlesme_gucu_kw: false,
  donem_tuketimi_kwh: false,
  gunluk_ortalama_kwh: false,
  tarife: false,
};

export default function Sayfa() {
  const [adim, setAdim] = useState<Adim>(0);
  const [calisiyor, setCalisiyor] = useState(false);
  const [hata, setHata] = useState<string | null>(null);

  const [ev, setEv] = useState<EvGirdisi>(BOS_EV);
  const [otomatik, setOtomatik] = useState(HICBIRI);
  const [onayliEv, setOnayliEv] = useState<EvGirdisi | null>(null);
  const [sonuc, setSonuc] = useState<OneriSonucu | null>(null);

  async function gorselleriAnalizEt(sayac: File, fatura: File) {
    setCalisiyor(true);
    setHata(null);
    try {
      const analiz = await evAnaliziIste(sayac, fatura);
      setEv(analiz.home);
      // Dolu dönen her alan "otomatik okundu" sayılır; boş olanı kullanıcı girer.
      setOtomatik({
        faz: analiz.home.faz !== "belirsiz",
        sozlesme_gucu_kw: analiz.home.sozlesme_gucu_kw !== null,
        donem_tuketimi_kwh: analiz.home.donem_tuketimi_kwh !== null,
        gunluk_ortalama_kwh: analiz.home.gunluk_ortalama_kwh !== null,
        tarife: analiz.home.tarife !== null,
      });
      setAdim(1);
    } catch (h) {
      setHata(h instanceof Error ? h.message : "Görsel analizi başarısız.");
    } finally {
      setCalisiyor(false);
    }
  }

  function elleGir() {
    setEv(BOS_EV);
    setOtomatik(HICBIRI);
    setHata(null);
    setAdim(1);
  }

  async function degerlendir(vehicleId: string, kullanim: Kullanim) {
    if (!onayliEv) return;
    setCalisiyor(true);
    setHata(null);
    try {
      const yanit = await oneriIste({
        home: onayliEv,
        vehicle_id: vehicleId,
        user: kullanim,
        // Adım 2'den geçilmeden buraya gelinemez; onay oradan alınır.
        kullanici_onayladi: true,
      });
      setSonuc(yanit);
      setAdim(3);
    } catch (h) {
      setHata(h instanceof Error ? h.message : "Değerlendirme başarısız.");
    } finally {
      setCalisiyor(false);
    }
  }

  return (
    <>
      <Baslik aktif={adim} />
      <Govde>
        {hata && <Hata mesaj={hata} />}

        {adim === 0 && (
          <AdimYukleme
            onAnaliz={gorselleriAnalizEt}
            onElleGir={elleGir}
            calisiyor={calisiyor}
          />
        )}

        {adim === 1 && (
          <AdimOnay
            baslangic={ev}
            otomatik={otomatik}
            onOnay={(onaylanan) => {
              setOnayliEv(onaylanan);
              setHata(null);
              setAdim(2);
            }}
            onGeri={() => setAdim(0)}
          />
        )}

        {adim === 2 && (
          <AdimArac
            onDegerlendir={degerlendir}
            onGeri={() => setAdim(1)}
            calisiyor={calisiyor}
          />
        )}

        {adim === 3 && sonuc && (
          <AdimSonuc sonuc={sonuc} onGeri={() => setAdim(2)} />
        )}
      </Govde>
      <Altbilgi>
        {adim === 3
          ? "Buradaki güçler aracınız ile ünite arasındaki teorik sınırdır; evinizin panosunun bunu taşıyıp taşımadığı ayrıca doğrulanmalıdır."
          : undefined}
      </Altbilgi>
    </>
  );
}
