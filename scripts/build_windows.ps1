param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $ProjectRoot

if ($Clean) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "build", "dist"
}

python -B scripts/check_syntax.py
python -B scripts/check_locales.py
python -B scripts/check_resources.py
python -B -c "import svg_icon_studio.app; import svg_icon_studio.ui.main_window; print('Import check passed.')"
python -B scripts/prepare_icons.py --require
pyinstaller --noconfirm --clean SVGIconStudio.spec

$ReleaseDir = Join-Path $ProjectRoot "release"
New-Item -ItemType Directory -Force $ReleaseDir | Out-Null
$ZipPath = Join-Path $ReleaseDir "SVGIconStudio-Windows.zip"
Remove-Item -Force -ErrorAction SilentlyContinue $ZipPath
Compress-Archive -Path "dist/SVGIconStudio" -DestinationPath $ZipPath
Write-Host "Windows ZIP created: $ZipPath"
