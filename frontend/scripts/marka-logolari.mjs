/**
 * Katalogdaki marka adlarını `simple-icons` paketiyle eşleştirip
 * `app/lib/marka-logolari.json` dosyasını üretir.
 *
 * Çalıştırma:  npm run logolar
 *
 * Üretilen dosya depoya işlenir; uygulama çalışırken simple-icons paketinin
 * tamamını (3000'den fazla ikon) pakete dahil etmemek için bu yol seçildi.
 * Eşleşmeyen markalar arayüzde harf monogramıyla gösterilir.
 */

import { writeFileSync, readFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import * as simpleIcons from "simple-icons";

const BURASI = dirname(fileURLToPath(import.meta.url));
const BACKEND_DATA = resolve(BURASI, "../../backend/data");
const HEDEF = resolve(BURASI, "../app/lib/marka-logolari.json");

/** Aksan, noktalama ve büyük/küçük harf farklarını siler. */
const anahtar = (metin) =>
  String(metin)
    .replace(/[İIı]/g, "i")
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .replace(/[^a-z0-9]/g, "");

const ikonlar = new Map();
for (const ikon of Object.values(simpleIcons)) {
  if (ikon && typeof ikon === "object" && ikon.title && ikon.path) {
    const k = anahtar(ikon.title);
    if (!ikonlar.has(k)) ikonlar.set(k, ikon);
  }
}

const oku = (dosya) =>
  JSON.parse(readFileSync(resolve(BACKEND_DATA, dosya), "utf8").replace(/^﻿/, ""));

const markalar = new Set();
for (const kayit of oku("ARAC_KDS_CEKIRDEK_100.json")) markalar.add(kayit.marka);
for (const kayit of oku("WALLBOX_KDS_CEKIRDEK_30_V1_1.json")) markalar.add(kayit.marka);

const cikti = {};
const eslesmeyen = [];
for (const marka of [...markalar].sort()) {
  const ikon = ikonlar.get(anahtar(marka));
  if (ikon) cikti[marka] = ikon.path;
  else eslesmeyen.push(marka);
}

mkdirSync(dirname(HEDEF), { recursive: true });
writeFileSync(HEDEF, JSON.stringify(cikti, null, 1) + "\n", "utf8");

console.log(`${Object.keys(cikti).length}/${markalar.size} marka eşleşti → ${HEDEF}`);
if (eslesmeyen.length) console.log("Monogram kullanılacak:", eslesmeyen.join(", "));
