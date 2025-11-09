# xai/services/generator_llama.py
from typing import Dict, List, Any
from threading import Lock

# Try both likely import paths. Adjust if your file lives elsewhere.
try:
    # e.g. icare/backend/carebot/response_generator_llama.py
    from carebot.response_generator_llama import generate_response
except Exception:
    # e.g. icare/backend/carebot/llama/response_generator_llama.py
    from carebot.response_generator_llama import generate_response  # type: ignore

# In-memory chat store for demo. Swap to DB later.
_CHAT: Dict[str, List[dict]] = {}
_LOCK = Lock()

# Keep the system prompt short and safe. Tailor if you like.
_SYSTEM_PROMPT = (
    "You are iCare, a calm, supportive psychotherapist. "
    "Respond briefly with empathy and one gentle question when helpful. "
    "Avoid medical claims or crisis advice. Keep language kind and clear."
)

def llama_reply(user_id: str, message: str, want_brief: bool = False) -> tuple[str, Dict[str, Any]]:
    """Call LLaMA via the project's generate_response and return reply + signals."""
    with _LOCK:
        history = _CHAT.setdefault(user_id, [])
        history = generate_response(_SYSTEM_PROMPT, message, history)
        # Persist a short history to bound memory
        _CHAT[user_id] = history[-8:]
        reply = _CHAT[user_id][-1]["text"] if _CHAT[user_id] else ""

    # Optional brevity trim for UI
    if want_brief and len(reply) > 400:
        reply = reply[:400].rstrip() + "…"

    gen_signals = {
        "feeling": "llama",           # tells the explainer this came from LLaMA
        "want_brief": want_brief,
        "used_snippet_ids": []        # we can still append retrieval ids if you keep retrieval
    }
    return reply, gen_signals
