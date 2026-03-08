$ErrorActionPreference = 'Stop'

param(
    [Parameter(Mandatory = $true)]
    [string]$ZipPath,

    [string]$StagingRoot = (Join-Path $PSScriptRoot '../90_tmp/unpack')
)

$ZipPath = [System.IO.Path]::GetFullPath($ZipPath)
$StagingRoot = [System.IO.Path]::GetFullPath($StagingRoot)

if (-not (Test-Path -LiteralPath $ZipPath)) {
    throw "ZIP not found: $ZipPath"
}

New-Item -ItemType Directory -Force -Path $StagingRoot | Out-Null
Expand-Archive -LiteralPath $ZipPath -DestinationPath $StagingRoot -Force
Write-Host "UNPACK_OK: $StagingRoot"
