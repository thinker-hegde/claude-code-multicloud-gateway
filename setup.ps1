# ==============================================================================
# Universal Multi-Cloud Gateway — Quick Launch Script (Windows PowerShell)
# ==============================================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "⚡ Universal Multi-Cloud Gateway for Claude Code" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Exit 1
}

# 2. Check and Validate $env: API Keys
Write-Host "`n[1/4] Checking Environment Variables ($env:)..." -ForegroundColor Yellow

$nvidiaKey = $env:NVIDIA_API_KEY
$groqKey = $env:GROQ_API_KEY
$geminiKey = $env:GEMINI_API_KEY

if ($nvidiaKey) {
    Write-Host "  -> Tier 1 (NVIDIA NIM): Detected ($($nvidiaKey.Substring(0, [Math]::Min(8, $nvidiaKey.Length)))...)" -ForegroundColor Green
} else {
    Write-Host "  -> Tier 1 (NVIDIA NIM): Not set (Get free key: https://build.nvidia.com)" -ForegroundColor DarkGray
}

if ($groqKey) {
    Write-Host "  -> Tier 2 (Groq Cloud): Detected ($($groqKey.Substring(0, [Math]::Min(8, $groqKey.Length)))...)" -ForegroundColor Green
} else {
    Write-Host "  -> Tier 2 (Groq Cloud): Not set (Get free key: https://console.groq.com/keys)" -ForegroundColor DarkGray
}

if ($geminiKey) {
    Write-Host "  -> Tier 3 (Google Gemini): Detected ($($geminiKey.Substring(0, [Math]::Min(8, $geminiKey.Length)))...)" -ForegroundColor Green
} else {
    Write-Host "  -> Tier 3 (Google Gemini): Not set (Get free key: https://aistudio.google.com)" -ForegroundColor DarkGray
}

# 3. Check Local Ollama Engine
Write-Host "`n[2/4] Checking Local Ollama Engine (Tier 4 Offline Fallback)..." -ForegroundColor Yellow
try {
    $ollamaRes = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    $localModels = $ollamaRes.models | ForEach-Object { $_.name }
    Write-Host "  -> Ollama Server: Running on http://127.0.0.1:11434 ✅" -ForegroundColor Green
    Write-Host "  -> Local Models: $($localModels -join ', ')" -ForegroundColor Cyan
} catch {
    Write-Host "  -> Ollama Server: Not detected. (Install from https://ollama.com for offline resilience)" -ForegroundColor DarkGray
}

# 4. Check Dependencies
Write-Host "`n[3/4] Verifying Python Dependencies..." -ForegroundColor Yellow
python -m pip install -q -r requirements.txt

# 5. Configure Claude Code settings.json
Write-Host "`n[4/4] Linking Claude Code Configuration..." -ForegroundColor Yellow
$claudeDir = Join-Path $HOME ".claude"
if (-not (Test-Path $claudeDir)) { New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null }

$settingsFile = Join-Path $claudeDir "settings.json"
$config = @{
    "model" = "nvidia/nemotron-3-super-120b-a12b"
    "env" = @{
        "ANTHROPIC_BASE_URL" = "http://127.0.0.1:8000"
        "ANTHROPIC_AUTH_TOKEN" = "multi-cloud-hybrid"
        "ANTHROPIC_MODEL" = "nvidia/nemotron-3-super-120b-a12b"
        "ANTHROPIC_DEFAULT_MODEL" = "nvidia/nemotron-3-super-120b-a12b"
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC" = "1"
        "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT" = "1"
    }
}
$config | ConvertTo-Json -Depth 4 | Set-Content -Path $settingsFile -Encoding utf8
Write-Host "  -> Claude Code settings registered successfully." -ForegroundColor Green

# 6. Start Gateway
Write-Host "`n🚀 Launching Gateway on http://127.0.0.1:8000..." -ForegroundColor Cyan
Write-Host "Open another terminal and run 'claude' to start coding!`n" -ForegroundColor Green
python main.py
