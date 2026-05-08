# build-prod-image.ps1 — A4 arbitrage 2026-04-23
# Produit l'image pli/backend:prod pour scan trivy M3.
# Source : docs/governance/arbitrages/2026-04-23-baseline-infra.md §A4
# Auteur : session M4.
#
# Pré-requis : Docker Desktop installé + démarré (status vert dans la tray).
# Télécharger : https://www.docker.com/products/docker-desktop/
#
# Usage :
#   1. Ouvrir Docker Desktop, attendre que le moteur soit prêt (icône verte).
#   2. Clic droit sur ce fichier → "Exécuter avec PowerShell".
#      (ou depuis PowerShell : cd <chemin backend> ; .\build-prod-image.ps1)
#   3. Laisser tourner ~3-5 min (premier build : ~8 min, pull python:3.11-slim).
#   4. À la fin, la taille + digest de l'image s'affichent.
#   5. Coller le digest dans le chat direction pour notifier M3.

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

Write-Host "=== A4 build pli/backend:prod ===" -ForegroundColor Cyan
Write-Host "Context : $PSScriptRoot" -ForegroundColor Gray
Write-Host ""

# --- 1. Verif Docker ---
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "[OK] $dockerVersion" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Docker non installe ou absent du PATH." -ForegroundColor Red
    Write-Host "       Installer Docker Desktop : https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "       Puis relancer ce script." -ForegroundColor Yellow
    exit 1
}

try {
    $dockerInfo = docker info --format '{{.ServerVersion}}' 2>&1
    if ($LASTEXITCODE -ne 0) { throw $dockerInfo }
    Write-Host "[OK] Docker daemon en route (server $dockerInfo)" -ForegroundColor Green
}
catch {
    Write-Host "[FAIL] Docker Desktop n'est pas demarre." -ForegroundColor Red
    Write-Host "       Ouvrir Docker Desktop et attendre l'icone verte, puis relancer." -ForegroundColor Yellow
    exit 1
}

# --- 2. Build ---
Write-Host ""
Write-Host "=== Build (cible runtime, multi-stage) ===" -ForegroundColor Cyan
Write-Host ""

$start = Get-Date
docker build --target runtime -t pli/backend:prod .
$exitCode = $LASTEXITCODE
$duration = (Get-Date) - $start

if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "[FAIL] Build echec (exit $exitCode). Voir logs Docker ci-dessus." -ForegroundColor Red
    exit $exitCode
}

Write-Host ""
Write-Host ("[OK] Build termine en {0:mm}m{0:ss}s." -f $duration) -ForegroundColor Green

# --- 3. Attestation ---
Write-Host ""
Write-Host "=== Attestation image ===" -ForegroundColor Cyan
Write-Host ""

$image = docker inspect pli/backend:prod --format '{{.Id}}|{{.Size}}|{{.RepoDigests}}|{{.Config.User}}|{{.Created}}' 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] docker inspect a echoue : $image" -ForegroundColor Yellow
}
else {
    $parts = $image -split '\|'
    $imageId = $parts[0]
    $sizeBytes = [int64]$parts[1]
    $sizeMb = [math]::Round($sizeBytes / 1MB, 1)
    $digests = $parts[2]
    $user = $parts[3]
    $created = $parts[4]

    Write-Host "Image ID     : $imageId"
    Write-Host "Taille       : ${sizeMb} MB"
    Write-Host "User         : $user"
    Write-Host "Cree le      : $created"
    Write-Host "RepoDigests  : $digests"
}

Write-Host ""
Write-Host "=== docker images pli/backend:prod ===" -ForegroundColor Cyan
docker images pli/backend:prod

Write-Host ""
Write-Host "Prochaine etape (M3) :" -ForegroundColor Cyan
Write-Host "  trivy image --severity CRITICAL,HIGH --ignore-unfixed pli/backend:prod"
Write-Host ""
Write-Host "Coller dans le chat direction :" -ForegroundColor Cyan
Write-Host "  - Image ID : $imageId"
Write-Host "  - Taille : ${sizeMb} MB"
Write-Host ""
Read-Host "Appuyer sur Entree pour fermer"
