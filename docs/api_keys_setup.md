# 🔑 Free Developer API Keys Setup Guide

This guide provides step-by-step instructions for generating 100% free developer API keys for **NVIDIA NIM**, **Groq Cloud**, and **Google Gemini API**, as well as configuring them in your environment.

---

## 1. NVIDIA NIM Cloud (Nemotron 3 Super 120B)
* **Tier**: Primary High-Reasoning Flagship (Tier 1)
* **Speed**: ~107.3 tokens/sec on NVIDIA H100 TensorRT-LLM cluster
* **Free Quota**: 1,000 Free Developer Credits on signup

### Steps to Generate:
1. Open **[build.nvidia.com](https://build.nvidia.com)** in your browser.
2. Sign in with your NVIDIA Developer account (or create a free account).
3. Search for or select **`nvidia/nemotron-3-super-120b-a12b`** (or open any NIM model page).
4. Click the green **"Get API Key"** button.
5. Copy your key (starts with `nvapi-...`).

---

## 2. Groq Cloud (GPT-OSS / Llama 120B & 70B)
* **Tier**: Ultra-Fast LPU Inference (Tier 2)
* **Speed**: 200–350+ tokens/sec on Groq LPU Custom Hardware
* **Free Quota**: 100% Free Forever (30 requests/minute)

### Steps to Generate:
1. Open **[console.groq.com/keys](https://console.groq.com/keys)**.
2. Sign in with your GitHub or Google account.
3. In the left navigation menu, click **"API Keys"**.
4. Click **"Create API Key"**, give it a name (e.g. `claude-gateway`), and click **Submit**.
5. Copy your key (starts with `gsk_...`).

---

## 3. Google Gemini API (Gemini 3.6 Flash)
* **Tier**: 1 Million Token Context Engine (Tier 3)
* **Speed**: ~150+ tokens/sec with massive codebase context
* **Free Quota**: 1,500 Requests / Day (100% Free Forever, resets every 24h)

### Steps to Generate:
1. Open **[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)**.
2. Sign in with your regular Google account.
3. Click the blue **"Create API key"** button.
4. Select **"Create in new project"** (or choose an existing GCP project).
5. Copy your key (starts with `AIzaSy...`).

---

## 4. Local Ollama (Qwen3-Coder 30B / 1.5B)
* **Tier**: 100% Offline & Private (Tier 4)
* **Speed**: 12–80 tokens/sec on local laptop hardware
* **Free Quota**: Unlimited Forever (Zero Internet Required)

### Steps to Setup:
1. Download Ollama from **[ollama.com](https://ollama.com)** and install it.
2. Open your terminal and pull the models:
   ```bash
   ollama pull qwen3-coder:30b
   ollama pull qwen2.5-coder:1.5b
   ```
3. Ollama runs locally on `http://127.0.0.1:11434`.

---

## ⚙️ How to Save Keys in Your System Environment

### 🪟 Windows PowerShell:
```powershell
[Environment]::SetEnvironmentVariable('NVIDIA_API_KEY', 'nvapi-your-key-here', 'User')
[Environment]::SetEnvironmentVariable('GROQ_API_KEY', 'gsk_your-key-here', 'User')
[Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'AIzaSy-your-key-here', 'User')
```

### 🐧 Linux / macOS:
Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export NVIDIA_API_KEY="nvapi-your-key-here"
export GROQ_API_KEY="gsk_your-key-here"
export GEMINI_API_KEY="AIzaSy-your-key-here"
```

### 📄 Or using `.env`:
Copy `.env.example` to `.env` in the repository root and paste your keys.
