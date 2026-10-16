import { ReactNode } from "react";

export const ADIM_ADLARI = ["Görseller", "Onay", "Araç", "Sonuç"] as const;

function Logo() {
  return (
    <span className="flex items-center gap-[11px]">
      <svg
        width="26"
        height="26"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.9"
        strokeLinecap="round"
        strokeLinejoin="round"
        className="text-vurgu"
        aria-hidden="true"
      >
        <path d="M3 10.5 12 3l9 7.5" />
        <path d="M5.5 9.5V20h13V9.5" />
        <path d="M12.8 11.5 10 15.4h3.4L11.2 19" />
      </svg>
      <span className="text-base font-semibold tracking-tight">EVCSDS</span>
    </span>
  );
}

function Adimlar({ aktif }: { aktif: number }) {
  return (
    <ol className="flex flex-wrap gap-x-[22px] gap-y-2 list-none m-0 p-0">
      {ADIM_ADLARI.map((ad, i) => {
        const gecildi = i < aktif;
        const simdi = i === aktif;
        return (
          <li
            key={ad}
            className={`flex items-center gap-2 text-[13.5px] ${
              simdi ? "font-semibold text-murekkep" : "text-murekkep-3"
            }`}
            aria-current={simdi ? "step" : undefined}
          >
            <span
              className={`w-[21px] h-[21px] rounded-full grid place-items-center font-mono text-[11.5px] font-semibold ${
                gecildi
                  ? "bg-uygun text-white"
                  : simdi
                    ? "bg-vurgu text-white"
                    : "bg-[#edebe6] text-murekkep-3"
              }`}
            >
              {i + 1}
            </span>
            {ad}
          </li>
        );
      })}
    </ol>
  );
}

export function Baslik({ aktif, sag }: { aktif: number; sag?: ReactNode }) {
  return (
    <header className="bg-kart border-b border-cizgi">
      <div className="max-w-[1060px] mx-auto px-6 sm:px-10 py-5 flex flex-wrap gap-4 items-center justify-between">
        <Logo />
        {sag ?? <Adimlar aktif={aktif} />}
      </div>
    </header>
  );
}

export function Altbilgi({ children }: { children?: ReactNode }) {
  return (
    <footer className="bg-kart border-t border-cizgi mt-auto">
      <div className="max-w-[1060px] mx-auto px-6 sm:px-10 py-[22px]">
        <p className="m-0 text-[13.5px] leading-relaxed text-murekkep-2 max-w-[820px]">
          <strong className="font-semibold text-murekkep">
            Bu sistem kurulum onayı vermez.
          </strong>{" "}
          {children ??
            "Sözleşme gücü, evinizin panosunun bir şarj ünitesini güvenle taşıyacağını kanıtlamaz. Kurulum için yetkili elektrik tesisatçısına danışın."}
        </p>
      </div>
    </footer>
  );
}

export function Govde({ children }: { children: ReactNode }) {
  return (
    <main className="flex-1 w-full max-w-[1060px] mx-auto px-6 sm:px-10 py-12 sm:py-16">
      {children}
    </main>
  );
}

export function Dugme({
  children,
  onClick,
  disabled,
  tur = "ana",
  tip = "button",
}: {
  children: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  tur?: "ana" | "ikincil";
  tip?: "button" | "submit";
}) {
  const ortak =
    "inline-flex items-center gap-2.5 px-7 min-h-[50px] rounded-xl text-base font-semibold transition-colors disabled:opacity-45 disabled:cursor-not-allowed";
  const stil =
    tur === "ana"
      ? "bg-vurgu text-white hover:bg-vurgu-koyu"
      : "bg-kart text-murekkep border border-cizgi-koyu font-medium hover:bg-[#faf9f7]";
  return (
    <button type={tip} onClick={onClick} disabled={disabled} className={`${ortak} ${stil}`}>
      {children}
    </button>
  );
}

export function Ok() {
  return (
    <svg
      width="17"
      height="17"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.3"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="M5 12h13" />
      <path d="m12.5 5.5 6.5 6.5-6.5 6.5" />
    </svg>
  );
}

export function Tik({ boyut = 13 }: { boyut?: number }) {
  return (
    <svg
      width={boyut}
      height={boyut}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d="m4.5 12.5 5 5 10-11" />
    </svg>
  );
}

export function Unlem({ boyut = 13 }: { boyut?: number }) {
  return (
    <svg
      width={boyut}
      height={boyut}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7.5v5.5" />
      <path d="M12 16.6h.01" />
    </svg>
  );
}

export function Hata({ mesaj }: { mesaj: string }) {
  return (
    <div
      role="alert"
      className="flex gap-3 bg-elenen-acik border border-[#f0c9c3] rounded-xl px-5 py-4 mb-6"
    >
      <span className="text-elenen-yazi flex-none mt-0.5">
        <Unlem boyut={18} />
      </span>
      <p className="m-0 text-[14.5px] leading-relaxed text-murekkep-2">{mesaj}</p>
    </div>
  );
}
