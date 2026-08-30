#!/bin/bash
# ==============================================================================
# Universal Multi-Cloud Gateway — Quick Launch Script (Linux / macOS)
# ==============================================================================

echo "========================================================"
echo "⚡ Universal Multi-Cloud Gateway for Claude Code"
echo "========================================================"

# 1. Install dependencies
echo -e "\n[1/3] Installing Python Dependencies..."
python3 -m pip install -q -r requirements.txt

# 2. Check environment variables
echo -e "\n[2/3] Checking Environment Variables..."
[ -n "$NVIDIA_API_KEY" ] && echo "  -> NVIDIA NIM Key: Detected" || echo "  -> NVIDIA NIM Key: Not set"
[ -n "$GROQ_API_KEY" ] && echo "  -> Groq Cloud Key: Detected" || echo "  -> Groq Cloud Key: Not set"
[ -n "$GEMINI_API_KEY" ] && echo "  -> Google Gemini Key: Detected" || echo "  -> Google Gemini Key: Not set"

# 3. Configure Claude Code
echo -e "\n[3/3] Linking Claude Code Configuration..."
mkdir -p "$HOME/.claude"
cat <<EOF > "$HOME/.claude/settings.json"
{
  "model": "nvidia/nemotron-3-super-120b-a12b",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:8000",
    "ANTHROPIC_AUTH_TOKEN": "multi-cloud-hybrid",
    "ANTHROPIC_MODEL": "nvidia/nemotron-3-super-120b-a12b",
    "ANTHROPIC_DEFAULT_MODEL": "nvidia/nemotron-3-super-120b-a12b",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT": "1"
  }
}
EOF

echo -e "\n🚀 Starting Gateway on http://127.0.0.1:8000..."
python3 main.py
