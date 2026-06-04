# Start FastAPI locally (requires MySQL + migrations + seed first)
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PYTHONPATH = "."
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 0.0.0.0 --port 8000
