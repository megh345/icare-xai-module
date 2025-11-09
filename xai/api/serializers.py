from rest_framework import serializers

class ChatIn(serializers.Serializer):
    user_id = serializers.CharField()
    message = serializers.CharField()
    want_brief = serializers.BooleanField(required=False, default=False)

class ChatOut(serializers.Serializer):
    reply = serializers.CharField()
    explanation = serializers.CharField()
    safety_level = serializers.CharField()
    used_snippets = serializers.ListField(child=serializers.DictField())

class FeedbackIn(serializers.Serializer):
    user_id = serializers.CharField()
    message_id = serializers.CharField()
    helpfulness = serializers.IntegerField(min_value=1, max_value=5)
    clarity = serializers.IntegerField(min_value=1, max_value=5)
    tone = serializers.IntegerField(min_value=1, max_value=5)
    notes = serializers.CharField(required=False, allow_blank=True)
