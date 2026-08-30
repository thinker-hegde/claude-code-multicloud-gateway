"""
FastAPI Server Application & Hardened Endpoint Handlers
"""

import asyncio
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn

from .config import load_environment_keys, mask_key
from .pruners import build_openai_messages, translate_anthropic_to_openai_tools
from .router import build_provider_stack, execute_failover_stream
from .streamers import generate_sse_events

logger = logging.getLogger("multicloud_gateway")

app = FastAPI(
    title="Universal Multi-Cloud AI Gateway for Claude Code",
    description="4-Tier Intelligent Auto-Failover AI Router with Turbo Boosters",
    version="1.1.0"
)

@app.get("/health")
@app.head("/health")
@app.get("/api/hello")
@app.head("/api/hello")
async def health():
    return Response(content="ok", status_code=200)

@app.get("/v1/models")
async def list_models():
    return {
        "data": [
            {"id": "auto-resilient-hybrid", "display_name": "NVIDIA 120B + Groq 120B + Gemini 3.6 + Local 30B"},
            {"id": "nvidia/nemotron-3-super-120b-a12b", "display_name": "NVIDIA Nemotron 3 Super 120B"},
            {"id": "openai/gpt-oss-120b", "display_name": "Groq LPU 120B"},
            {"id": "gemini-3.6-flash", "display_name": "Google Gemini 3.6 Flash"},
            {"id": "qwen3-coder:30b", "display_name": "Local Qwen3-Coder 30B"}
        ]
    }

@app.post("/v1/messages")
async def messages(request: Request):
    try:
        req_data = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse JSON body: {type(e).__name__}")
        return JSONResponse({"error": "invalid json body"}, status_code=400)

    keys = load_environment_keys()
    messages_input = req_data.get("messages", [])
    system_prompt = req_data.get("system", "")
    tools = req_data.get("tools", [])

    # Keep conversation sliding window bounded to prevent memory bloat
    if isinstance(messages_input, list) and len(messages_input) > 8:
        messages_input = messages_input[-8:]

    cloud_messages = build_openai_messages(messages_input, str(system_prompt), is_local=False)
    local_messages = build_openai_messages(messages_input, str(system_prompt), is_local=True)
    cloud_tools = translate_anthropic_to_openai_tools(tools if isinstance(tools, list) else [])

    queue = asyncio.Queue(maxsize=500)
    done_event = asyncio.Event()

    providers = build_provider_stack(keys, cloud_messages, local_messages, cloud_tools)
    worker_task = asyncio.create_task(execute_failover_stream(providers, queue, done_event))

    async def sse_wrapper():
        try:
            async for chunk in generate_sse_events(queue, done_event):
                yield chunk
        finally:
            if not worker_task.done():
                worker_task.cancel()

    return StreamingResponse(
        sse_wrapper(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

def main():
    keys = load_environment_keys()
    logger.info("Initializing Universal Multi-Cloud Gateway...")
    logger.info(f"  -> NVIDIA NIM Key: {mask_key(keys['NVIDIA_API_KEY'])}")
    logger.info(f"  -> Groq Cloud Key: {mask_key(keys['GROQ_API_KEY'])}")
    logger.info(f"  -> Gemini API Key: {mask_key(keys['GEMINI_API_KEY'])}")
    logger.info(f"  -> Ollama Host:    {keys['OLLAMA_HOST']}")
    logger.info(f"  -> Listening on:   http://{keys['HOST']}:{keys['PORT']}")
    
    uvicorn.run(app, host=keys["HOST"], port=keys["PORT"], log_level="warning")

if __name__ == "__main__":
    main()
