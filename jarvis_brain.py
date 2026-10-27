"""
jarvis_brain.py - Hybrid Cloud + Offline AI Brain with Rate Limit Failover
Uses free Groq endpoints for ultra-fast responses, and smoothly falls back
to offline local processing if API rate limits or network issues occur.
"""

import os
import json
import time
import re
from openai import OpenAI
import jarvis_actions

KEYFILE = os.path.expanduser("~/.openjarvis/free.key")
MODELS = ["openai/gpt-oss-20b", "llama-3.3-70b-versatile", "qwen/qwen3.8-27b"]

_client = None
_history = []
_cooldown_until = 0.0

SYSTEM_PROMPT = """You are Jarvis, a fast, highly capable AI executive assistant running on the user's computer.
Respond concisely in 1-2 sentences. Be direct, helpful, and natural. Do not use filler or formal corporate jargon.
"""


def _get_api_key():
    if os.environ.get("GROQ_API_KEY"):
        return os.environ["GROQ_API_KEY"].strip()
    if os.path.exists(KEYFILE):
        return open(KEYFILE).read().strip()
    return None


def ready():
    """Returns True if the cloud brain is active and not currently rate-limited."""
    key = _get_api_key()
    if not key:
        return False
    return time.time() >= _cooldown_until


def _is_rate_limited(e):
    status = getattr(e, "status_code", None)
    if status == 429:
        return True
    s = str(e).lower()
    return any(w in s for w in ("429", "rate limit", "too many requests", "rate_limit", "exceeded"))


def _retry_after_seconds(e, default=60):
    s = str(e).lower()
    m = re.search(r"try again in\s*(\d+)m\s*([0-9]+(?:\.[0-9]+)?)s", s)
    if m:
        return int(float(m.group(1)) * 60 + float(m.group(2))) + 2
    m = re.search(r"try again in\s*([0-9]+(?:\.[0-9]+)?)s", s)
    if m:
        return int(float(m.group(1))) + 2
    return default


def _set_cooldown(secs):
    global _cooldown_until
    _cooldown_until = max(_cooldown_until, time.time() + float(secs))


def _local_fallback(q):
    """
    Called when Groq API is temporarily rate-limited.
    Provides immediate local action execution or cached briefing without crashing.
    """
    # 1. Try deterministic local actions first
    action_res = jarvis_actions.try_action(q)
    if action_res:
        return action_res

    # 2. General intelligent local response
    return (
        "Cloud API is cooling down, but my local assistant is active. "
        "I can open your apps, check WhatsApp, or analyze stock charts for you."
    )


def think(q):
    """
    Main entry point for queries. Tries local actions first, then cloud AI,
    with automatic fallback if rate limited.
    """
    global _client, _history

    # 1. Immediate local action check
    local_done = jarvis_actions.try_action(q)
    if local_done:
        return local_done

    key = _get_api_key()
    if not key or time.time() < _cooldown_until:
        return _local_fallback(q)

    if _client is None:
        _client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + _history[-6:] + [{"role": "user", "content": q}]

    for model in MODELS:
        try:
            resp = _client.chat.completions.create(
                model=model,
                messages=msgs,
                max_tokens=350,
                temperature=0.6,
            )
            answer = resp.choices[0].message.content.strip()
            _history += [{"role": "user", "content": q}, {"role": "assistant", "content": answer}]
            return answer
        except Exception as e:
            if _is_rate_limited(e):
                wait_sec = _retry_after_seconds(e)
                _set_cooldown(wait_sec)
                print(f"[Rate-limit triggered: cooldown for {wait_sec}s]")
                return _local_fallback(q)
            print(f"[Model {model} failed: {e}]")

    return _local_fallback(q)


if __name__ == "__main__":
    print("Testing Jarvis Brain...")
    print(think("what time is it"))
    print(think("how are you"))
