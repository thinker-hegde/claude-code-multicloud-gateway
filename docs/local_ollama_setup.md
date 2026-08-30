# 🦙 Complete Local Ollama Setup & Turbo Booster Guide

This guide covers setting up **Local Ollama** as the **100% Offline & Private Tier 4 Engine** for Claude Code, explaining model sizing, GPU requirements, tool-calling capabilities, and the built-in **Turbo Boosters** that slash local latency.

---

## 🚀 The Local Turbo Boosters (How We Slashed Local Latency)

Running local LLMs inside Claude Code typically encounters severe latency bottlenecks. Our Gateway implements **3 Built-in Turbo Boosters** to make local execution ultra-fast:

### 1. ✂️ Smart System Prompt Pruning (25s ➡️ 0.2s TTFT)
* **The Problem**: Claude Code transmits a massive **5,000-token system prompt** (with dozens of markdown rules and constraints) on *every single chat turn*.
* On local CPU / RAM, processing 5,000 prefill tokens takes **15 to 30 seconds** before the first word is even output.
* **The Turbo Fix**: When routing to Ollama, the gateway automatically intercepts and condenses the 5,000-token prompt down to essential instructions. **Time-To-First-Token drops from 25s to 0.2s!**

---

### 2. ⚡ Causal Attention vs. SWA (Instant Turn-to-Turn Caching)
* **The Problem**: Models like Gemma 4 26B use *Sliding Window Attention (SWA)*, which causes Ollama / `llama.cpp` to invalidate the KV cache and re-process the entire conversation history on every turn (45s delay per message).
* **The Turbo Fix**: By selecting **Qwen3-Coder (30B MoE)** and **Qwen2.5-Coder (1.5B/7B)**, which use standard Causal Attention, Ollama reuses **100% of the KV cache across turns**, giving instant `< 1s` turn-to-turn execution.

---

### 3. 🧩 Smart Tool Schema Compression
* Claude Code injects 30 verbose tool definitions into the prompt.
* Small local models (< 7B) get overwhelmed by 5,000-token schemas and hallucinate raw JSON strings (e.g. `{"name": "Glob", "arguments": ...}`) into chat text.
* The Gateway prunes tool schemas down to concise 2-line JSON schemas (`ReadFile`, `WriteFile`, `EditFile`, `Bash`), allowing **`qwen3-coder:30b` to execute tools natively without crashing**.

---

## 📊 Model Sizing & GPU Requirements

| Model | Size | RAM / VRAM Req | Speed | Tool-Calling Reliability | Best Use Case |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`qwen3-coder:30b`** | ~18 GB | 16–32 GB RAM | **10–14 tok/s** | 🟢 **Full Multi-Turn Agentic** | Autonomous workspace editing & refactoring |
| **`qwen2.5-coder:7b`** | ~4.5 GB | 8 GB RAM / 4GB VRAM | **25–40 tok/s** | 🟡 **Moderate** | Standard file edits & function generation |
| **`qwen2.5-coder:1.5b`** | ~1.2 GB | 2 GB VRAM (100% GPU) | **70–90 tok/s** ⚡ | 🔴 **Code Only** | Ultra-fast single-turn function writing |

---

## 🛠️ Step-by-Step Local Setup

### 1. Install Ollama
* **Windows / macOS / Linux**: Download from [ollama.com](https://ollama.com).

### 2. Pull Recommended Models
Run in your terminal:
```powershell
# Flagship Agentic Coding Model (Recommended for Tools)
ollama pull qwen3-coder:30b

# Ultra-Fast GPU Model (80+ tok/s on 100% GPU VRAM)
ollama pull qwen2.5-coder:1.5b
```

### 3. Verify Ollama is Running
Open `http://127.0.0.1:11434` in your browser. You should see:
```text
Ollama is running
```

---

## ✈️ Testing Offline Airplane Mode
To verify offline resilience:
1. Turn off your Wi-Fi / disconnect your network.
2. Open your terminal and run `claude`.
3. Ask Claude Code:
   ```text
   > Read architecture.html and add a search box component
   ```
4. The **Gateway will automatically detect the offline state and route directly to your local Ollama engine** without dropping your prompt!
