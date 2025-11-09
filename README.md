# icare-xai-module
Explainable AI for iCare

Explainability layer for a mental health support chatbot. This repo contains only the XAI components I wrote. The core chatbot remains private and is not included here.

# iCare Explainability Module (XAI)
This repository contains the explainability layer developed for the iCare mental health chatbot.

The module provides:
- “Why this?” explanations for chatbot replies
- Template-based, emotionally safe responses
- Integration-ready endpoints for SHAP and attention-based explainability

Structure
- `api/` – Django API views for explanations
- `services/` – Explainability logic, retrieval, safety
- `data/` – Supporting files or configs
- `logs/` – Local logging outputs for debugging

## What this module does
- Builds short, human friendly “Why this?” explanations for a given chatbot reply
- Uses policy templates to keep language safe and predictable
- Optionally attaches brief psychoeducation notes from vetted sources

## What this module does not do
- It doesn’t diagnose or provide medical advice
- It doesn’t include any of the original chatbot code

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python demo/run_demo.py

```
### 📁 Folder Overview
- **xai/api/** — REST API endpoints for chatbot and explanations  
- **xai/services/** — Core logic (safety, retrieval, generation, explainability)  
- **xai/data/** — Stores configurations or small datasets (no sensitive data)  
- **xai/logs/** — Logs generated during experiments  
- **demo/** — A lightweight example showing module integration  


## Django App Creation
To create the XAI module inside your chatbot project:
```bash
python manage.py startapp xai
mkdir -p xai/api xai/services xai/data xai/logs
touch xai/api/__init__.py xai/api/serializers.py xai/api/views.py
touch xai/services/__init__.py xai/services/safety.py xai/services/retrieval.py xai/services/generator.py xai/services/explainability.py
touch xai/urls.py xai/tests.py
```
# xai/services/explainability.py
"""
Explainability module:
Builds user-facing explanations ('Why this?') for chatbot responses.
Integrates with SHAP/attention outputs where applicable.
"""
