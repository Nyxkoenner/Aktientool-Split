$ErrorActionPreference = "Stop"

function Invoke-PythonModule {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Module,
        [Parameter(ValueFromRemainingArguments = $true)]
        [string[]]$Arguments
    )

    Write-Host ""
    Write-Host "==> python -m $Module $($Arguments -join ' ')" -ForegroundColor Cyan
    & python -m $Module @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Prüfschritt fehlgeschlagen: python -m $Module $($Arguments -join ' ')"
    }
}

Invoke-PythonModule pytest
Invoke-PythonModule ruff format --check stock_explorer tests
Invoke-PythonModule ruff check stock_explorer tests
Invoke-PythonModule mypy stock_explorer/providers stock_explorer/domain stock_explorer/services
Invoke-PythonModule py_compile app.py stock_explorer/legacy_app.py

Write-Host ""
Write-Host "Alle Qualitätsprüfungen waren erfolgreich." -ForegroundColor Green
