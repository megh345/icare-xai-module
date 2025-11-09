from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import ChatIn, ChatOut, FeedbackIn
from xai.services.safety import screen_message
from xai.services.retrieval import retrieve
from xai.services.explainability import build_explanation
import os, json
from datetime import datetime
from rest_framework import status

# Feature flag: use LLaMA or rule-based
USE_LLAMA = os.environ.get("XAI_USE_LLAMA", "1").lower() in ("1", "true", "yes")
if USE_LLAMA:
    from xai.services.llama_adapter import llama_reply
else:
    from xai.services.generator import generate_reply

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
FB_PATH = os.path.join(LOG_DIR, "feedback.jsonl")

@api_view(["POST"])
@permission_classes([AllowAny])
def chat(request):
    s = ChatIn(data=request.data)
    s.is_valid(raise_exception=True)
    data = s.validated_data

    # Safety screen
    safety = screen_message(data["message"])
    if safety["level"] == "crisis":
        payload = {
    "reply": reply,
    "explanation": explanation,
    "safety_level": "ok",
    "used_snippets": hits,
    "salient_tokens": top,   # <-- include when you compute it here instead of inside build_explanation
}
        return Response(ChatOut(payload).data)

    # Retrieval (optional snippets for rationale)
    hits = retrieve(data["message"], k=3)

    # Generate reply
    if USE_LLAMA:
        reply, gen_signals = llama_reply(
            data["user_id"], data["message"], want_brief=data["want_brief"]
        )
    else:
        reply, gen_signals = generate_reply(
            data["message"], hits, want_brief=data["want_brief"]
        )

    # Build user-facing explanation
    explanation = build_explanation(
        user_msg=data["message"], hits=hits, gen_signals=gen_signals
    )

    payload = {
        "reply": reply,
        "explanation": explanation,
        "safety_level": "ok",
        "used_snippets": hits
    }
    return Response(ChatOut(payload).data)

@api_view(["POST"])
@permission_classes([AllowAny])
def feedback(request):
    s = FeedbackIn(data=request.data)
    s.is_valid(raise_exception=True)
    rec = {**s.validated_data, "ts": datetime.utcnow().isoformat()}
    with open(FB_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return Response({"ok": True})


@api_view(["POST"])
@permission_classes([AllowAny])
def attention(request):
    text = (request.data or {}).get("text", "")
    if not text.strip():
        return Response({"detail": "missing text"}, status=400)
    from xai.services.attention import get_attention_for_message
    return Response(get_attention_for_message(text))

@api_view(["POST"])
@permission_classes([AllowAny])
def importance(request):
    """
    Return token-level importance using Integrated Gradients.
    Body: {"text": "..."}
    """
    try:
        data = request.data or {}
        text = (data.get("text") or "").strip()
        if not text:
            return Response({"tokens": [], "scores": []})

        from xai.services.attribution import tokens_and_ig_scores
        tokens, scores = tokens_and_ig_scores(text)
        return Response({"tokens": tokens, "scores": scores})
    except Exception as e:
        # keep the API resilient
        return Response(
            {"error": f"importance failed: {type(e).__name__}: {e}"},
            status=500,
        )





# ...your other imports...
# we'll reuse the same tokenizer/importance logic you already have
# If you have a helper that returns (tokens, scores), import it here.
# Otherwise this fallback uses whitespace tokenization.

def _simple_token_importance(text: str):
    """
    Fallback: very simple tokenization + heuristic importance.
    Replace this with your gradient-based tokenizer if available.
    Returns (tokens, scores in [0,1]).
    """
    words = [w for w in text.strip().split() if w]
    if not words:
        return [], []
    # Heuristic: longer & “emotional” words get more weight
    emo = {"hopeless", "anxious", "exhausted", "stressed", "overwhelmed", "burnout"}
    raw = []
    for w in words:
        base = max(1, len(w))
        if w.lower().strip(".,!?") in emo:
            base *= 2.0
        raw.append(float(base))
    mx = max(raw) if raw else 1.0
    scores = [r / mx for r in raw]
    return words, scores

@api_view(["POST"])
@permission_classes([AllowAny])
def attention(request):
    """
    Returns an attention heatmap for the input text.

    Success payload:
    {
      "tokens": [...],
      "attn": [[...], ...],      # NxN list (rows = query tokens, cols = key tokens)
      "note": "native" | "fallback"
    }
    """
    text = (request.data or {}).get("text", "")
    if not text.strip():
        return Response({"tokens": [], "attn": []})

    # Try your native attention implementation first
    try:
        # If you built a helper, import/use it here:
        # from chatbots.carebot.xai_attention import tokens_and_attention
        # tokens, attn = tokens_and_attention(text)
        # return Response({"tokens": tokens, "attn": attn, "note": "native"})

        # If you don't have a native extractor yet, raise to hit the fallback:
        raise ModuleNotFoundError("native attention extractor not wired yet")
    except ModuleNotFoundError:
        # ---- Fallback: derive a symmetric “attention-like” matrix
        tokens, scores = _simple_token_importance(text)
        if not tokens:
            return Response({"tokens": [], "attn": []})
        # Normalize and build outer-product heatmap
        try:
            import numpy as np
            s = np.array(scores, dtype=float)
            if s.max() > 0:
                s = s / s.max()
            M = np.outer(s, s).tolist()
        except Exception:
            # No numpy? build it by hand
            mx = max(scores) or 1.0
            s = [x / mx for x in scores]
            M = [[si * sj for sj in s] for si in s]

        return Response({"tokens": tokens, "attn": M, "note": "fallback"}, status=status.HTTP_200_OK)

