"""
Multi-Cloud 4-Tier Auto-Failover Routing Engine with Hardened Security
"""

import logging
import asyncio
import httpx

logger = logging.getLogger("multicloud_gateway")

def build_provider_stack(keys: dict, cloud_messages: list, local_messages: list, cloud_tools: list) -> list:
    """
    Builds the 4-tier provider failover priority list:
    1. NVIDIA NIM (120B Super Model)
    2. Groq Cloud (120B / 70B LPU)
    3. Google Gemini (Gemini 3.6 Flash / 1M Context)
    4. Local Ollama (Qwen3-Coder 30B Turbo / Offline)
    """
    providers = []

    # Tier 1: NVIDIA NIM (Flagship 120B)
    if keys["NVIDIA_API_KEY"]:
        providers.append({
            "name": "Tier 1: NVIDIA NIM (Nemotron 3 Super 120B)",
            "type": "openai",
            "url": "https://integrate.api.nvidia.com/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {keys['NVIDIA_API_KEY']}", "Content-Type": "application/json"},
            "payload": {
                "model": "nvidia/nemotron-3-super-120b-a12b",
                "messages": cloud_messages,
                "temperature": 0.2,
                "max_tokens": 4096,
                "stream": True,
                **({"tools": cloud_tools} if cloud_tools else {})
            }
        })

    # Tier 2: Groq Cloud LPU (120B)
    if keys["GROQ_API_KEY"]:
        providers.append({
            "name": "Tier 2: Groq LPU (GPT-OSS 120B)",
            "type": "openai",
            "url": "https://api.groq.com/openai/v1/chat/completions",
            "headers": {"Authorization": f"Bearer {keys['GROQ_API_KEY']}", "Content-Type": "application/json"},
            "payload": {
                "model": "openai/gpt-oss-120b",
                "messages": cloud_messages,
                "temperature": 0.2,
                "max_tokens": 4096,
                "stream": True,
                **({"tools": cloud_tools} if cloud_tools else {})
            }
        })

    # Tier 3: Google Gemini API (1M Context)
    if keys["GEMINI_API_KEY"]:
        gemini_contents = []
        for om in cloud_messages:
            g_role = "model" if om["role"] in ["assistant", "system"] else "user"
            gemini_contents.append({"role": g_role, "parts": [{"text": om["content"]}]})

        providers.append({
            "name": "Tier 3: Google Gemini 3.6 Flash",
            "type": "gemini",
            "url": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:streamGenerateContent?alt=sse&key={keys['GEMINI_API_KEY']}",
            "headers": {"Content-Type": "application/json"},
            "payload": {
                "contents": gemini_contents,
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 4096}
            }
        })

    # Tier 4: Local Ollama (100% Offline & Private)
    providers.append({
        "name": "Tier 4: Local Ollama (Qwen3-Coder 30B Turbo)",
        "type": "ollama",
        "url": f"{keys['OLLAMA_HOST']}/api/chat",
        "headers": {"Content-Type": "application/json"},
        "payload": {
            "model": "qwen3-coder:30b",
            "messages": local_messages,
            "stream": True,
            "options": {
                "temperature": 0.2,
                "num_ctx": 16384,
                "num_predict": 4096,
                "low_vram": False
            }
        }
    })

    return providers

async def execute_failover_stream(providers: list, queue: asyncio.Queue, done_event: asyncio.Event):
    """
    Attempts providers sequentially in priority order.
    Automatically fails over upon HTTP error, rate limit, or network disconnection.
    Ensures zero secret leakage in logs.
    """
    try:
        for provider in providers:
            try:
                logger.info(f"Connecting to {provider['name']}...")
                # Enforce safe 120s timeout per attempt
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream("POST", provider["url"], headers=provider["headers"], json=provider["payload"]) as response:
                        if response.status_code == 200:
                            logger.info(f"Active Provider: {provider['name']} [STREAMING]")
                            async for line in response.aiter_lines():
                                if line:
                                    await queue.put((provider["type"], line))
                            return
                        else:
                            logger.warning(f"{provider['name']} returned HTTP {response.status_code}. Auto-failing over...")
            except asyncio.CancelledError:
                logger.info(f"Request cancelled by client during {provider['name']} stream.")
                return
            except Exception as ex:
                # Log safe error class without leaking raw request objects
                logger.warning(f"{provider['name']} connection error ({type(ex).__name__}). Auto-failing over...")
    finally:
        done_event.set()
