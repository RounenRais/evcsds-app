# EVCSDS kurulum ve çalıştırma — Windows PowerShell
#
#   .\kur.ps1              kurar ve iki sunucuyu da başlatır
#   .\kur.ps1 -SadeceKur   yalnız kurar, başlatmaz
#   .\kur.ps1 -Backend     yalnız backend (npm install gerekmez, ~250 MB tasarruf)
#
# Görsel analiz (fatura/sayaç fotoğrafı yükleme) için ek kurulum gerekir;
# birkaç GB yer kaplar ve bu script onu kurmaz:
#   pip install -r backend\requirements-vision.txt

param(
    [switch]$SadeceKur,
    [switch]$Backend
)

$ErrorActionPreference = "Stop"
$Kok = $PSScriptRoot

function Adim($metin) { Write-Host "`n==> $metin" -ForegroundColor Cyan }
function Tamam($metin) { Write-Host "    $metin" -ForegroundColor Green }

# --- Gereksinimler ------------------------------------------------------
Adim "Gereksinimler denetleniyor"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "python bulunamadı. https://www.python.org/downloads/ adresinden kurun."
}
Tamam (python --version)
if (-not $Backend) {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        throw "node bulunamadı. https://nodejs.org adresinden kurun, ya da -Backend ile yalnız backend'i çalıştırın."
    }
    Tamam ("node " + (node --version))
}

# --- Backend ------------------------------------------------------------
Adim "Backend kuruluyor"
$Venv = Join-Path $Kok "backend\.venv"
if (-not (Test-Path $Venv)) {
    python -m venv $Venv
    Tamam "sanal ortam oluşturuldu"
} else {
    Tamam "sanal ortam zaten var"
}

$Py = Join-Path $Venv "Scripts\python.exe"
& $Py -m pip install --quiet --upgrade pip
& $Py -m pip install --quiet -r (Join-Path $Kok "backend\requirements.txt")
Tamam "python paketleri hazır"

$Keys = Join-Path $Kok "backend\keys.json"
if (-not (Test-Path $Keys)) {
    Copy-Item (Join-Path $Kok "backend\keys.example.json") $Keys
    Tamam "keys.json oluşturuldu"
}

# --- Motor doğrulaması --------------------------------------------------
Adim "Karar motoru doğrulanıyor (85 senaryo)"
Push-Location (Join-Path $Kok "backend")
& $Py -B -m kds_engine.run_benchmark | Select-String "Kontroller"
Pop-Location

# --- Frontend -----------------------------------------------------------
if (-not $Backend) {
    Adim "Frontend kuruluyor (ilk seferde birkaç dakika sürebilir)"
    Push-Location (Join-Path $Kok "frontend")
    if (-not (Test-Path "node_modules")) {
        npm install --no-audit --no-fund
    } else {
        Tamam "node_modules zaten var"
    }
    if (-not (Test-Path ".env.local")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env.local"
        } else {
            # Örnek dosya elde yoksa varsayılanlarla üret; kurulum yarıda kalmasın.
            @(
                "NEXT_PUBLIC_API_URL=http://localhost:8000",
                "EVCSDS_API_URL=http://localhost:8000",
                "EVCSDS_API_KEY="
            ) | Set-Content -Encoding UTF8 ".env.local"
        }
        Tamam ".env.local oluşturuldu"
    }
    Pop-Location
}

if ($SadeceKur) {
    Write-Host "`nKurulum bitti. Başlatmak için: .\kur.ps1" -ForegroundColor Green
    exit 0
}

# --- Başlat -------------------------------------------------------------
Adim "Sunucular başlatılıyor"
$BackendKomut = "cd '$Kok\backend'; & '$Py' -m uvicorn main:app --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $BackendKomut
Tamam "backend  -> http://localhost:8000/docs"

if (-not $Backend) {
    $FrontendKomut = "cd '$Kok\frontend'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $FrontendKomut
    Tamam "frontend -> http://localhost:3000"
    Start-Sleep -Seconds 6
    Start-Process "http://localhost:3000"
} else {
    Start-Sleep -Seconds 3
    Start-Process "http://localhost:8000/docs"
}

Write-Host "`nHazır. Fotoğrafsız denemek için arayüzde 'Bilgileri elle gireceğim' bağlantısını kullanın." -ForegroundColor Green
