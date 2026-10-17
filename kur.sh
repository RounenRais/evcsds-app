#!/usr/bin/env bash
# EVCSDS kurulum ve çalıştırma — macOS / Linux
#
#   ./kur.sh               kurar ve iki sunucuyu da başlatır
#   ./kur.sh --sadece-kur  yalnız kurar, başlatmaz
#   ./kur.sh --backend     yalnız backend (npm install gerekmez, ~250 MB tasarruf)
#
# Görsel analiz için ek kurulum gerekir; birkaç GB yer kaplar ve bu script
# onu kurmaz:  pip install -r backend/requirements-vision.txt

set -euo pipefail

KOK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SADECE_KUR=0
SADECE_BACKEND=0
for arg in "$@"; do
  case "$arg" in
    --sadece-kur) SADECE_KUR=1 ;;
    --backend) SADECE_BACKEND=1 ;;
    *) echo "Bilinmeyen seçenek: $arg" >&2; exit 2 ;;
  esac
done

adim() { printf '\n\033[36m==> %s\033[0m\n' "$1"; }
tamam() { printf '\033[32m    %s\033[0m\n' "$1"; }

# --- Gereksinimler ------------------------------------------------------
adim "Gereksinimler denetleniyor"
command -v python3 >/dev/null || { echo "python3 bulunamadı." >&2; exit 1; }
tamam "$(python3 --version)"
if [ "$SADECE_BACKEND" -eq 0 ]; then
  command -v node >/dev/null || {
    echo "node bulunamadı. --backend ile yalnız backend'i çalıştırabilirsiniz." >&2
    exit 1
  }
  tamam "node $(node --version)"
fi

# --- Backend ------------------------------------------------------------
adim "Backend kuruluyor"
VENV="$KOK/backend/.venv"
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
  tamam "sanal ortam oluşturuldu"
else
  tamam "sanal ortam zaten var"
fi

PY="$VENV/bin/python"
"$PY" -m pip install --quiet --upgrade pip
"$PY" -m pip install --quiet -r "$KOK/backend/requirements.txt"
tamam "python paketleri hazır"

if [ ! -f "$KOK/backend/keys.json" ]; then
  cp "$KOK/backend/keys.example.json" "$KOK/backend/keys.json"
  tamam "keys.json oluşturuldu"
fi

# --- Motor doğrulaması --------------------------------------------------
adim "Karar motoru doğrulanıyor (85 senaryo)"
(cd "$KOK/backend" && "$PY" -B -m kds_engine.run_benchmark | grep "Kontroller")

# --- Frontend -----------------------------------------------------------
if [ "$SADECE_BACKEND" -eq 0 ]; then
  adim "Frontend kuruluyor (ilk seferde birkaç dakika sürebilir)"
  cd "$KOK/frontend"
  if [ ! -d node_modules ]; then
    npm install --no-audit --no-fund
  else
    tamam "node_modules zaten var"
  fi
  if [ ! -f .env.local ]; then
    if [ -f .env.example ]; then
      cp .env.example .env.local
    else
      # Örnek dosya elde yoksa varsayılanlarla üret; kurulum yarıda kalmasın.
      cat > .env.local <<'ENV'
NEXT_PUBLIC_API_URL=http://localhost:8000
EVCSDS_API_URL=http://localhost:8000
EVCSDS_API_KEY=
ENV
    fi
    tamam ".env.local oluşturuldu"
  fi
  cd "$KOK"
fi

if [ "$SADECE_KUR" -eq 1 ]; then
  printf '\n\033[32mKurulum bitti. Başlatmak için: ./kur.sh\033[0m\n'
  exit 0
fi

# --- Başlat -------------------------------------------------------------
adim "Sunucular başlatılıyor"
temizle() { kill ${PIDLER[@]} 2>/dev/null || true; }
trap temizle EXIT INT TERM
PIDLER=()

(cd "$KOK/backend" && exec "$PY" -m uvicorn main:app --port 8000) &
PIDLER+=($!)
tamam "backend  -> http://localhost:8000/docs"

if [ "$SADECE_BACKEND" -eq 0 ]; then
  (cd "$KOK/frontend" && exec npm run dev) &
  PIDLER+=($!)
  tamam "frontend -> http://localhost:3000"
fi

printf '\n\033[32mHazır. Durdurmak için Ctrl+C.\033[0m\n'
printf 'Fotoğrafsız denemek için arayüzde "Bilgileri elle gireceğim" bağlantısını kullanın.\n'
wait
