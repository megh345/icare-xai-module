from chatbots.carebot.attn_utils import extract_attention
def get_attention_for_message(message: str):
    return extract_attention(message, max_len=64)
