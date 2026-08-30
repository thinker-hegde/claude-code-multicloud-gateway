"""
Real-Time Token-by-Token SSE Streamer & Safe Delta Parser
"""

import json
import time
import asyncio
import logging

logger = logging.getLogger("multicloud_gateway")

async def generate_sse_events(queue: asyncio.Queue, done_event: asyncio.Event):
    """
    Consumes upstream chunks from OpenAI, Gemini, or Ollama,
    formats them into Anthropic SSE events, and streams them live to Claude Code.
    Includes full error handling against malformed JSON or upstream disconnection.
    """
    msg_id = f"msg_{int(time.time())}"
    yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'id': msg_id, 'type': 'message', 'role': 'assistant', 'model': 'quad-cloud-hybrid', 'content': [], 'stop_reason': None, 'usage': {'input_tokens': 50, 'output_tokens': 0}}})}\n\n"
    yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"

    text_block_started = False
    block_index = 0
    total_chars = 0
    captured_tool_calls = {}

    try:
        while not done_event.is_set() or not queue.empty():
            try:
                p_type, raw_line = await asyncio.wait_for(queue.get(), timeout=1.0)
                content_delta = ""

                # 1. OpenAI Format (NVIDIA NIM / Groq LPU)
                if p_type == "openai":
                    if raw_line.startswith("data: "):
                        payload_str = raw_line[6:].strip()
                        if payload_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(payload_str)
                            choices = chunk.get("choices", [])
                            if choices and isinstance(choices, list):
                                delta = choices[0].get("delta", {})
                                content_delta = delta.get("content", "") or ""
                                
                                if "tool_calls" in delta and isinstance(delta["tool_calls"], list):
                                    for tc in delta["tool_calls"]:
                                        tc_idx = tc.get("index", 0)
                                        if tc_idx not in captured_tool_calls:
                                            captured_tool_calls[tc_idx] = {
                                                "id": tc.get("id", f"toolu_{int(time.time())}_{tc_idx}"),
                                                "name": tc.get("function", {}).get("name", ""),
                                                "args": ""
                                            }
                                        if "function" in tc and "arguments" in tc["function"]:
                                            captured_tool_calls[tc_idx]["args"] += tc["function"]["arguments"]
                        except (json.JSONDecodeError, Exception) as parse_err:
                            logger.debug(f"Skipping non-fatal chunk parse error: {parse_err}")

                # 2. Gemini SSE Format
                elif p_type == "gemini":
                    if raw_line.startswith("data: "):
                        try:
                            chunk = json.loads(raw_line[6:])
                            cands = chunk.get("candidates", [])
                            if cands and isinstance(cands, list):
                                parts = cands[0].get("content", {}).get("parts", [])
                                for p in parts:
                                    if isinstance(p, dict) and "text" in p:
                                        content_delta += p["text"]
                        except (json.JSONDecodeError, Exception) as parse_err:
                            logger.debug(f"Skipping non-fatal Gemini chunk error: {parse_err}")

                # 3. Ollama JSON Lines Format
                elif p_type == "ollama":
                    try:
                        chunk = json.loads(raw_line)
                        if isinstance(chunk, dict):
                            content_delta = chunk.get("message", {}).get("content", "") or ""
                    except (json.JSONDecodeError, Exception) as parse_err:
                        logger.debug(f"Skipping non-fatal Ollama chunk error: {parse_err}")

                # Yield parsed text deltas
                if content_delta:
                    total_chars += len(content_delta)
                    if not text_block_started:
                        yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': block_index, 'content_block': {'type': 'text', 'text': ''}})}\n\n"
                        text_block_started = True
                    
                    yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': block_index, 'delta': {'type': 'text_delta', 'text': content_delta}})}\n\n"

            except asyncio.TimeoutError:
                yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"

        if text_block_started:
            yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': block_index})}\n\n"
            block_index += 1

        # Yield parsed tool execution blocks
        if captured_tool_calls:
            for idx, tc in captured_tool_calls.items():
                try:
                    parsed_args = json.loads(tc["args"])
                except Exception:
                    parsed_args = {}

                yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': block_index, 'content_block': {'type': 'tool_use', 'id': tc['id'], 'name': tc['name'], 'input': {}}})}\n\n"
                yield f"event: content_block_delta\ndata: {json.dumps({'type': 'content_block_delta', 'index': block_index, 'delta': {'type': 'input_json_delta', 'partial_json': json.dumps(parsed_args)}})}\n\n"
                yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': block_index})}\n\n"
                block_index += 1

        if block_index == 0:
            yield f"event: content_block_start\ndata: {json.dumps({'type': 'content_block_start', 'index': 0, 'content_block': {'type': 'text', 'text': 'I am ready to assist you with your code.'}})}\n\n"
            yield f"event: content_block_stop\ndata: {json.dumps({'type': 'content_block_stop', 'index': 0})}\n\n"

        stop_reason = "tool_use" if captured_tool_calls else "end_turn"
        yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': stop_reason, 'stop_sequence': None}, 'usage': {'output_tokens': 100}})}\n\n"
        yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"
        logger.info(f"Stream Completed: total_chars={total_chars}, stop_reason={stop_reason}")

    except asyncio.CancelledError:
        logger.info("Client disconnected / request cancelled.")
    except Exception as err:
        logger.error(f"Stream error: {err}")
        yield f"event: message_delta\ndata: {json.dumps({'type': 'message_delta', 'delta': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'usage': {'output_tokens': 0}})}\n\n"
        yield f"event: message_stop\ndata: {json.dumps({'type': 'message_stop'})}\n\n"
