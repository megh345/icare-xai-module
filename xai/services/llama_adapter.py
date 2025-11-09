# backend/xai/services/llama_adapter.py
from __future__ import annotations
from typing import Dict, List, Tuple
from chatbots.carebot.response_generator_llama import generate_response

# Very simple in-memory history per user for the demo
_USER_HISTORY: Dict[str, List[Dict[str, str]]] = {}

_SYSTEM_PROMPT = (
    "You are iCare, a calm, supportive psychotherapist. "
    "Respond briefly with empathy and, when helpful, ask one gentle question. "
    "Avoid medical claims or crisis advice. Keep language kind and clear."
)

def _feeling_hint(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["anxious", "anxiety", "worry", "panic"]):
        return "anxiety"
    if any(w in t for w in ["sad", "low", "hopeless", "down"]):
        return "low_mood"
    if any(w in t for w in ["sleep", "insomnia", "tired", "exhausted"]):
        return "sleep"
    return "general"

def llama_reply(user_id: str, message: str, want_brief: bool = False) -> Tuple[str, Dict]:
    """
    Returns (reply, gen_signals) where gen_signals is passed to the XAI explainer.
    """
    history = _USER_HISTORY.setdefault(user_id, [])
    # Call the model wrapper to update history with the new exchange
    updated_history = generate_response(_SYSTEM_PROMPT, message, history)

    # Last assistant turn is our reply
    reply = ""
    if updated_history and updated_history[-1].get("type") == "carebot":
        reply = updated_history[-1].get("text", "")

    # Persist history
    _USER_HISTORY[user_id] = updated_history

    gen_signals = {
        "system_prompt": _SYSTEM_PROMPT,
        "history": updated_history[:-1],  # exclude the just-produced assistant turn
        "want_brief": want_brief,
        "feeling": _feeling_hint(message),
    }
    return reply, gen_signals
