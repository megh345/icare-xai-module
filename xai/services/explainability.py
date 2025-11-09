from typing import List, Dict, Any
from chatbots.carebot.xai_saliency import token_saliency

FRIENDLY_REASONS = {
    "llama":   "I used your words to shape a short, supportive reply.",
    "low_mood": "You mentioned feeling low, so I suggested simple steps that can ease that feeling.",
    "anxiety":  "Your words pointed to worry and tension, so I offered calm-breathing and focus tips.",
    "sleep":    "Sleep came up in your message, so I shared ideas that help many people wind down.",
    "general":  "You asked for support, so I aimed for practical, gentle suggestions.",
}

def _snippet_reason(hits: List[Dict[str, Any]]) -> str:
    if not hits:
        return ""
    top = hits[0]
    if "tag" in top:
        return f"I included a short note from a trusted resource on {top['tag']} because it matched what you raised."
    return "I included a short note that matched your message."

def get_salient_tokens(user_msg: str, gen_signals: Dict[str, Any], k: int = 5) -> List[Dict[str, Any]]:

    # Return [{'token': str, 'score': float}, ...] for the tokens in the user's message that most influenced the reply. 
    # Safe to call even if signals are missing; will return [] on failure.
 
    try:
        system_prompt = (gen_signals or {}).get("system_prompt") or ""
        history = (gen_signals or {}).get("history", []) or []
        return token_saliency(system_prompt, user_msg, history, top_k=k) or []
    except Exception:
        return []

def build_explanation(user_msg: str, hits: List[Dict[str, Any]], gen_signals: Dict[str, Any]) -> str:

    # Compose a friendly, user-facing explanation string.
   
    parts: List[str] = []

    feeling = (gen_signals or {}).get("feeling", "general")
    parts.append(FRIENDLY_REASONS.get(feeling, FRIENDLY_REASONS["general"]))

    if (gen_signals or {}).get("want_brief"):
        parts.append("You asked for a brief answer, so I kept it concise.")

    # Optional: include salient words if available
    top = get_salient_tokens(user_msg, gen_signals, k=5)
    if top:
        words = ", ".join(t["token"] for t in top if t.get("token"))
        parts.append(f"I focused on words like {words} because they stood out most strongly.")

    snip = _snippet_reason(hits)
    if snip:
        parts.append(snip)

    parts.append("If I’ve missed the mark, tell me what to focus on and I’ll adjust.")

    return " ".join(parts)
