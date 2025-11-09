# backend/xai/services/attribution.py
from __future__ import annotations
from typing import List, Tuple
import torch
from captum.attr import IntegratedGradients

# we reuse your LLaMA loader so we get the same model/tokenizer as the chat flow
from chatbots.carebot import get_llama_pipeline


@torch.no_grad()
def _pick_target_token_id(model, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> int:
    """
    Do a normal forward pass to choose a reasonable scalar target for IG:
    the argmax logit at the last position. This makes the attribution
    about 'the next-token the model is predicting given the input'.
    """
    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
    last_logits = outputs.logits[:, -1, :]            # [B, V]
    target_id = int(torch.argmax(last_logits, dim=-1)[0].item())
    return target_id


def tokens_and_ig_scores(text: str, steps: int = 32) -> Tuple[List[str], List[float]]:
    """
    Compute token-level attribution for `text` using Integrated Gradients
    against the model's next-token prediction at the final position.

    Returns (tokens, scores) where scores are in [0,1].
    """
    # 1) load model & tokenizer (same as chat)
    pipe, tok = get_llama_pipeline()
    model = pipe.model
    model.eval()

    device = next(model.parameters()).device

    # 2) tokenize
    enc = tok(
        text,
        return_tensors="pt",
        add_special_tokens=True,
        padding=False,
        truncation=True,
    )
    input_ids = enc["input_ids"].to(device)          # [1, L]
    attention_mask = enc["attention_mask"].to(device)

    # 3) target token (scalar objective for IG)
    
    # Option A: explain the classification head output (if you have one)
    # logits = classification_model(text)  # e.g. [positive, negative]
    # target_idx = logits.argmax(dim=-1).item()

    # Option B: force IG to attribute towards a word like "hopeless"
    target_word = "hopeless"
    target_id = tok.encode(target_word, add_special_tokens=False)[0]

    # 4) build a forward fn that takes embeddings
    emb_layer = model.get_input_embeddings()

    def fwd_with_emb(inputs_embeds: torch.Tensor, attn_mask: torch.Tensor):
        # outputs: logits [B, L, V]
        out = model(inputs_embeds=inputs_embeds, attention_mask=attn_mask)
        last_logits = out.logits[:, -1, :]                # [B, V]
        # gather scalar logit for our chosen target token
        return last_logits[:, target_id]                  # [B]

    # 5) inputs_embeds & baseline (zeros)
    with torch.no_grad():
        inputs_embeds = emb_layer(input_ids)              # [1, L, D]
    baseline = torch.zeros_like(inputs_embeds)

    # 6) run IG
    ig = IntegratedGradients(lambda emb: fwd_with_emb(emb, attention_mask))
    attributions = ig.attribute(
        inputs=inputs_embeds.requires_grad_(True),
        baselines=baseline,
        n_steps=steps,
        internal_batch_size=None,   # adjust if memory is tight
    )                               # [1, L, D]

    # 7) reduce over embedding dim → per-token score
    token_attr = attributions.sum(dim=-1).squeeze(0)      # [L]
    token_attr = token_attr.abs()

    # 8) normalise to [0,1] (avoid div by zero)
    maxv = float(token_attr.max().item()) if token_attr.numel() else 0.0
    if maxv > 0:
        token_attr = token_attr / maxv

    # 9) tokens for display
    tokens = tok.convert_ids_to_tokens(input_ids[0].tolist())
    scores = token_attr.detach().cpu().tolist()

    return tokens, scores

