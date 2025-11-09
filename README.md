# icare-xai-module
Explainable AI for iCare

Explainability layer for a mental health support chatbot. This repo contains only the XAI components I wrote. The core chatbot remains private and is not included here.

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
