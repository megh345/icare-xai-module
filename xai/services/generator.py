from typing import List, Dict, Any

LOW_MOOD = {"sad", "down", "low", "empty", "tired", "hopeless", "worthless"}
ANXIETY  = {"anxious", "worry", "worried", "panic", "overthink", "fear"}
SLEEP    = {"sleep", "insomnia", "awake"}

def _detect_feeling(msg: str) -> str:
    m = msg.lower()
    if any(w in m for w in LOW_MOOD): return "low_mood"
    if any(w in m for w in ANXIETY):  return "anxiety"
    if any(w in m for w in SLEEP):    return "sleep"
    return "general"

def generate_reply(user_msg: str, hits: List[Dict[str, Any]], want_brief: bool=False):
    feeling = _detect_feeling(user_msg)
    lines = []

    if feeling == "low_mood":
        lines.append("I’m sorry you’re feeling low. You’re not alone in this.")
        lines.append("Try one small step, like a short walk or texting someone you trust.")
    elif feeling == "anxiety":
        lines.append("That sounds stressful. Try a slow 4-in, 6-out breath for a minute.")
        lines.append("Pick one thing you can control in the next hour and do only that.")
    elif feeling == "sleep":
        lines.append("Sleep struggles are tough. Keeping lights dim and phones away for 30 minutes can help.")
    else:
        lines.append("Thanks for sharing. I’ll keep this practical and gentle.")

    if hits:
        lines.append(hits[0]["text"])

    reply = " ".join(lines[:2] if want_brief else lines)
    gen_signals = {
        "feeling": feeling,
        "want_brief": want_brief,
        "used_snippet_ids": [h["id"] for h in hits]
    }
    return reply, gen_signals
