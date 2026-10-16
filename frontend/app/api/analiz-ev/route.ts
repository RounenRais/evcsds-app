/** Görsel analiz vekili.
 *
 * API anahtarı yalnızca sunucuda durur ve tarayıcıya hiçbir zaman gönderilmez.
 * Tarayıcı iki dosyayı buraya yollar, burası anahtarı ekleyip backend'e iletir.
 */

import { NextRequest, NextResponse } from "next/server";

const API_TABANI = process.env.EVCSDS_API_URL ?? "http://localhost:8000";
const API_KEY = process.env.EVCSDS_API_KEY;

export async function POST(istek: NextRequest) {
  if (!API_KEY) {
    return NextResponse.json(
      {
        detail:
          "Sunucuda EVCSDS_API_KEY tanımlı değil. .env.local dosyasına ekleyin.",
      },
      { status: 503 }
    );
  }

  const form = await istek.formData();
  if (!(form.get("meter_file") instanceof File) || !(form.get("bill_file") instanceof File)) {
    return NextResponse.json(
      { detail: "Sayaç ve fatura görsellerinin ikisi de gerekli." },
      { status: 400 }
    );
  }

  let yanit: Response;
  try {
    yanit = await fetch(`${API_TABANI}/analyze/home`, {
      method: "POST",
      headers: { "X-API-Key": API_KEY },
      body: form,
    });
  } catch {
    return NextResponse.json(
      { detail: "Analiz sunucusuna ulaşılamadı." },
      { status: 502 }
    );
  }

  const govde = await yanit.json().catch(() => ({
    detail: "Analiz sunucusu okunabilir bir yanıt döndürmedi.",
  }));
  return NextResponse.json(govde, { status: yanit.status });
}
