"""
Configuration and Environment Variable Loader with Security Protections
"""

import os
import sys
import winreg
import logging

logger = logging.getLogger("multicloud_gateway")

ESSENTIAL_TOOLS = {
    "bash", "view", "edit", "fileread", "fileedit", "readfile", 
    "writefile", "glob", "grep", "readnotebook", "taskcreate", "tasklist"
}

def mask_key(key: str) -> str:
    """Safely masks API keys for logging without exposing full secrets."""
    if not key:
        return "None"
    if len(key) <= 8:
        return "***"
    return f"{key[:4]}...{key[-4:]}"

def load_environment_keys() -> dict:
    """
    Dynamically loads API keys from Windows Registry, .env files, and OS environment variables.
    Zero hardcoded tokens.
    """
    # Optional dotenv support
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    env_vars = {}
    if sys.platform == "win32":
        for hive, path in [
            (winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"),
            (winreg.HKEY_CURRENT_USER, "Environment")
        ]:
            try:
                k = winreg.OpenKey(hive, path)
                i = 0
                while True:
                    try:
                        name, val, _ = winreg.EnumValue(k, i)
                        env_vars[name] = val
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(k)
            except Exception:
                pass

    combined = {**os.environ, **env_vars}
    host = combined.get("HOST", "127.0.0.1").strip()
    
    # Security check: Warn if bound to external interface
    if host in ["0.0.0.0", "::"]:
        logger.warning(
            "[SECURITY NOTICE] Gateway is bound to 0.0.0.0 (all network interfaces). "
            "Ensure you trust all devices on your local network."
        )

    return {
        "NVIDIA_API_KEY": combined.get("NVIDIA_API_KEY", "").strip(),
        "GROQ_API_KEY": combined.get("GROQ_API_KEY", "").strip(),
        "GEMINI_API_KEY": (combined.get("GEMINI_API_KEY") or combined.get("GOOGLE_API_KEY") or "").strip(),
        "OLLAMA_HOST": combined.get("OLLAMA_HOST", "http://127.0.0.1:11434").strip(),
        "PORT": int(combined.get("PORT", 8000)),
        "HOST": host
    }
