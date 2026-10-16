/** Backend tipleri ve istemcisi.
 *
 * Katalog ve öneri uçları API anahtarı istemez, tarayıcıdan doğrudan çağrılır.
 * Görsel analiz ucu anahtar ister; anahtarın tarayıcıya düşmemesi için
 * `app/api/analiz-ev` sunucu tarafı vekili üzerinden geçer.
 */

export const API_TABANI =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Faz = "monofaz" | "trifaz" | "belirsiz";
export type KurulumYeri = "İç mekan" | "Dış mekan";

export interface EvGirdisi {
  faz: Faz;
  sozlesme_gucu_kw: number | null;
  donem_tuketimi_kwh: number | null;
  gunluk_ortalama_kwh: number | null;
  tarife: string | null;
}

export interface EvAnalizi {
  home: EvGirdisi;
  durum: "kullanici_onayi_gerekli" | "manuel_dogrulama_gerekli";
  manuel_dogrulama_alanlari: string[];
  onay_bekleyen_alanlar: string[];
  kdsye_dogrudan_aktarilabilir: boolean;
  uyari: string;
}

export interface Arac {
  vehicle_id: string;
  marka: string;
  model: string;
  ac_konnektor_tipi: string | null;
  ac_tek_faz_azami_guc_kw: number | null;
  ac_uc_faz_azami_guc_kw: number | null;
  batarya_kullanilabilir_kwh: number | null;
  wltp_tuketim_kwh_100km: number | null;
  wltp_menzil_km: number | null;
}

export interface Wallbox {
  charger_id: string;
  marka: string;
  model: string;
  nominal_azami_guc_kw: number | null;
  ac_konnektor_tipi: string | null;
  baglanti_tipi: string | null;
  kablo_uzunlugu_m: number | null;
  ip_sinifi: string | null;
  dinamik_yuk_yonetimi_destegi: string | null;
  fiyat_tl: number | null;
  fiyat_tarihi: string | null;
  garanti_yil: number | null;
}

export interface Metrikler {
  gunluk_arac_enerji_ihtiyaci_kwh: number | null;
  arac_wallbox_teorik_etkin_guc_kw: number | null;
  teorik_gunluk_ihtiyac_karsilama_suresi_saat: number | null;
  gunluk_ihtiyac_karsilama_orani: number | null;
  nominal_kapasite_kullanim_orani: number | null;
  fiyat_butce_orani: number | null;
}

export interface Aday {
  charger_id: string;
  urun: Wallbox;
  durum: "DEGERLENDIR" | "ELE" | "DOGRULAMA_GEREKLI" | "VERI_YETERSIZ";
  gerekceler: string[];
  eksik_alanlar: string[];
  uyarilar: string[];
  metrikler: Metrikler | null;
}

export type GrupAdi = "uygun" | "dogrulanmali" | "elenen" | "veri_yetersiz";

export interface Kullanim {
  gunluk_ortalama_km: number | null;
  evde_sarj_icin_uygun_sure_saat: number | null;
  butce_tl: number | null;
  kurulum_yeri: KurulumYeri;
}

export interface OneriSonucu {
  girdi: {
    home: EvGirdisi;
    arac: {
      vehicle_id: string;
      marka: string;
      model: string;
      ac_tek_faz_azami_guc_kw: number | null;
      ac_uc_faz_azami_guc_kw: number | null;
      wltp_tuketim_kwh_100km: number | null;
    };
    user: Kullanim;
  };
  sayilar: Record<GrupAdi, number>;
  toplam_degerlendirilen: number;
  gruplar: Record<GrupAdi, Aday[]>;
  siralama_yapilmadi: boolean;
  uyari: string;
}

class ApiHatasi extends Error {}

async function istek<T>(yol: string, secenekler?: RequestInit): Promise<T> {
  let yanit: Response;
  try {
    yanit = await fetch(`${API_TABANI}${yol}`, secenekler);
  } catch {
    throw new ApiHatasi(
      "Sunucuya ulaşılamadı. Backend çalışıyor mu kontrol edin."
    );
  }
  if (!yanit.ok) {
    const govde = await yanit.json().catch(() => null);
    throw new ApiHatasi(
      typeof govde?.detail === "string"
        ? govde.detail
        : `Sunucu ${yanit.status} döndü.`
    );
  }
  return yanit.json() as Promise<T>;
}

export function aracAra(sorgu: string, limit = 24): Promise<{ sayi: number; araclar: Arac[] }> {
  const p = new URLSearchParams({ limit: String(limit) });
  if (sorgu.trim()) p.set("q", sorgu.trim());
  return istek(`/catalog/vehicles?${p}`);
}

export function oneriIste(govde: {
  home: EvGirdisi;
  vehicle_id: string;
  user: Kullanim;
  kullanici_onayladi: boolean;
}): Promise<OneriSonucu> {
  return istek("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(govde),
  });
}

/** Görsel analizi sunucu tarafı vekili üzerinden çağırır. */
export async function evAnaliziIste(
  sayac: File,
  fatura: File
): Promise<EvAnalizi> {
  const form = new FormData();
  form.append("meter_file", sayac);
  form.append("bill_file", fatura);

  const yanit = await fetch("/api/analiz-ev", { method: "POST", body: form });
  if (!yanit.ok) {
    const govde = await yanit.json().catch(() => null);
    throw new ApiHatasi(
      typeof govde?.detail === "string" ? govde.detail : "Görsel analizi başarısız."
    );
  }
  return yanit.json();
}

/* ----------------------------- biçimlendirme ----------------------------- */

const sayiBicimi = new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 2 });

export const sayi = (deger: number | null | undefined, birim = ""): string =>
  deger === null || deger === undefined
    ? "—"
    : `${sayiBicimi.format(deger)}${birim ? ` ${birim}` : ""}`;

export const paraTl = (deger: number | null | undefined): string =>
  deger === null || deger === undefined
    ? "kayıt yok"
    : `${new Intl.NumberFormat("tr-TR", { maximumFractionDigits: 0 }).format(deger)} ₺`;

export const yuzde = (oran: number | null | undefined): string =>
  oran === null || oran === undefined ? "—" : `%${Math.round(oran * 100)}`;
