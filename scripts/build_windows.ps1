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
if ($LASTEXITCODE -ne 0) { throw "Validation or build failed" }
python -B scripts/check_locales.py
if ($LASTEXITCODE -ne 0) { throw "Validation or build failed" }
python -B scripts/check_resources.py
if ($LASTEXITCODE -ne 0) { throw "Validation or build failed" }
python -B -c "import svg_icon_studio.app; import svg_icon_studio.ui.main_window; print('Import check passed.')"
if ($LASTEXITCODE -ne 0) { throw "Validation or build failed" }
python -B scripts/prepare_icons.py --require
if ($LASTEXITCODE -ne 0) { throw "Validation or build failed" }
$env:QT_QPA_PLATFORM = "offscreen"
python -B -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "Regression tests failed" }
pyinstaller --noconfirm --clean SVGIconStudio.spec
if ($LASTEXITCODE -ne 0) { throw "Validation or build failed" }
$env:QT_QPA_PLATFORM = "offscreen"
$Process = Start-Process -FilePath "dist/SVGIconStudio/SVGIconStudio.exe" -ArgumentList "--self-test" -Wait -PassThru
if ($Process.ExitCode -ne 0) { throw "Packaged application self-test failed" }

$ReleaseDir = Join-Path $ProjectRoot "release"
New-Item -ItemType Directory -Force $ReleaseDir | Out-Null
$ZipPath = Join-Path $ReleaseDir "SVGIconStudio-Windows.zip"
Remove-Item -Force -ErrorAction SilentlyContinue $ZipPath
Compress-Archive -Path "dist/SVGIconStudio" -DestinationPath $ZipPath
Write-Host "Windows ZIP created: $ZipPath"
