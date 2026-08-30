# ⚡ How to Setup Claude Code Without Signing In (Zero-Login Guide)

This guide explains how to install and configure **Claude Code** to run entirely through the **Universal Multi-Cloud Gateway** without needing an Anthropic paid account, credit card, or browser login.

---

## 💡 How the Zero-Login Bypass Works

Normally, when you run `claude` for the first time, it attempts to open a browser window to authenticate with Anthropic and requests a paid subscription/API credit.

When you point Claude Code to your local gateway (`http://127.0.0.1:8000`) and provide a dummy `ANTHROPIC_AUTH_TOKEN`, Claude Code recognizes that it is in a **custom enterprise proxy environment** and **completely skips the browser OAuth sign-in flow**!

---

## 🛠️ Step-by-Step Zero-Login Setup

### 1. Install Claude Code CLI
Install Claude Code globally via `npm` (requires Node.js 18+):
```bash
npm install -g @anthropic-ai/claude-code
```

---

### 2. Configure `~/.claude/settings.json`
Create or edit the configuration file in your home directory:

* **Windows**: `C:\Users\<YourUsername>\.claude\settings.json`
* **Linux / macOS**: `~/.claude/settings.json`

Paste the following configuration:
```json
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
```

> **Why this works:**  
> * `ANTHROPIC_BASE_URL` redirects all API calls to your local gateway on port 8000.  
> * `ANTHROPIC_AUTH_TOKEN` satisfies Claude Code's internal authentication check without contacting Anthropic servers.

---

### 3. Launch the Gateway
Start your local Multi-Cloud Gateway:
```bash
python gateway.py
```
*(Or on Windows, run `.\setup.ps1` which creates the settings file automatically).*

---

### 4. Run Claude Code Directly
Open a new terminal in any project directory and run:
```bash
claude
```

You will see Claude Code start immediately without asking for a browser login, credit card, or Anthropic account. You can now use all file reading, writing, editing, and bash execution features with 120B cloud and local models!
