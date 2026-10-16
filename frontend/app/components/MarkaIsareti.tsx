import logolar from "../lib/marka-logolari.json";

const LOGOLAR = logolar as Record<string, string>;

/** Logosu olmayan markalar için harf monogramı üretir. */
function monogram(marka: string): string {
  const parcalar = marka.split(/[\s\-/]+/).filter(Boolean);
  if (parcalar.length >= 2) {
    return (parcalar[0][0] + parcalar[1][0]).toLocaleUpperCase("tr");
  }
  return marka.slice(0, 2).toLocaleUpperCase("tr");
}

export default function MarkaIsareti({
  marka,
  secili = false,
  boyut = 46,
}: {
  marka: string;
  secili?: boolean;
  boyut?: number;
}) {
  const yol = LOGOLAR[marka];
  const renk = secili ? "text-vurgu" : "text-[#2b2f36]";

  return (
    <span
      className={`flex-none grid place-items-center rounded-xl ${
        secili ? "bg-vurgu-acik" : "bg-[#f2f1ed]"
      }`}
      style={{ width: boyut, height: boyut }}
    >
      {yol ? (
        <svg
          viewBox="0 0 24 24"
          width={boyut / 2}
          height={boyut / 2}
          className={renk}
          role="img"
          aria-label={marka}
        >
          <path d={yol} fill="currentColor" />
        </svg>
      ) : (
        <span
          className={`font-bold ${renk}`}
          style={{ fontSize: boyut / 3.4 }}
          aria-label={marka}
          role="img"
        >
          {monogram(marka)}
        </span>
      )}
    </span>
  );
}
