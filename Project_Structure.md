# Project Structure Details

## Django App Creation
To create the XAI module inside your chatbot project:
```bash
python manage.py startapp xai
mkdir -p xai/api xai/services xai/data xai/logs
touch xai/api/__init__.py xai/api/serializers.py xai/api/views.py
touch xai/services/__init__.py xai/services/safety.py xai/services/retrieval.py xai/services/generator.py xai/services/explainability.py
touch xai/urls.py xai/tests.py
