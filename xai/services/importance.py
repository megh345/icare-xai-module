from chatbots.carebot.importance_utils import token_importance
def get_importance_for_message(message: str):
    return token_importance(message, max_len=64)
