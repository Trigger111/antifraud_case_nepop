param(
    [string]$Repository = "Trigger111/antifraud_case_nepop",
    [string]$Tag = "data-v1",
    [string]$AssetDirectory = "..\github_release_data"
)

$ErrorActionPreference = "Stop"
$resolvedAssets = Resolve-Path -LiteralPath $AssetDirectory
$files = @(
    "activity_log.parquet",
    "credits.parquet",
    "payments.parquet",
    "registrations.parquet"
) | ForEach-Object {
    Join-Path $resolvedAssets $_
}

foreach ($file in $files) {
    if (-not (Test-Path -LiteralPath $file)) {
        throw "Missing release asset: $file"
    }
}

gh release create $Tag @files `
    --repo $Repository `
    --title "Reproducibility data (Parquet)" `
    --notes "ZSTD-compressed Parquet files required to reproduce case3_antifraud.ipynb."
