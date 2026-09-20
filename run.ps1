param([switch]$Check)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    throw "未安装 uv。"
}

uv sync --locked
if ($LASTEXITCODE -ne 0) { throw "依赖同步失败" }

if ($Check) {
    uv run python scripts/check.py
    exit $LASTEXITCODE
}

foreach ($name in @("OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET", "OAUTH_JWT_SECRET")) {
    if ([string]::IsNullOrWhiteSpace([Environment]::GetEnvironmentVariable($name))) {
        throw "未设置 $name。"
    }
}

uv run uvicorn app.main:app --host 127.0.0.1 --port 8008
