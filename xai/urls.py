from django.urls import path
from xai.api.views import chat, feedback, attention, importance

urlpatterns = [
    path("chat", chat, name="xai-chat"),
    path("feedback", feedback, name="xai-feedback"),
     path("attn", attention),          
    path("importance", importance),   
]

