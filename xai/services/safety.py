import re

CRISIS_TERMS = [
    r"\bkill myself\b", r"\bsuicide\b", r"\bend my life\b",
    r"\bharm myself\b", r"\bno reason to live\b"
]

def screen_message(text: str):
    lower = text.lower()
    for pat in CRISIS_TERMS:
        if re.search(pat, lower):
            return {
                "level": "crisis",
                "crisis_message": (
                    "I’m really glad you told me. Your safety matters. "
                    "If you’re in immediate danger, call your local emergency number now. "
                    "In the U.S., you can contact the Suicide and Crisis Lifeline on 988. "
                    "If you prefer text, message 988 or use chat at 988lifeline.org."
                )
            }
    return {"level": "ok"}
