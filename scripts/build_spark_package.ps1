$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DistDir = Join-Path $ProjectRoot "dist"
$ZipPath = Join-Path $DistDir "nyc_taxi_project.zip"

New-Item -ItemType Directory -Force -Path $DistDir | Out-Null

if (Test-Path $ZipPath) {
    Remove-Item -LiteralPath $ZipPath -Force
}

Compress-Archive `
    -Path (Join-Path $ProjectRoot "config"), (Join-Path $ProjectRoot "src") `
    -DestinationPath $ZipPath `
    -Force

Write-Output "Spark package created: $ZipPath"
