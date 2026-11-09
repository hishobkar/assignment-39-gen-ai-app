---
title: GenAI Chat Assistant
emoji: 🤖
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.39.0
app_file: app.py
pinned: false
---

# 🤖 GenAI Chat Assistant

A Streamlit chat app with streaming responses, session-state chat history,
adjustable settings, and secure secret handling. Works with Google Gemini or OpenAI.

## Run locally
```bash
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then add your key
streamlit run app.py
```

## Deploy
- **Streamlit Cloud:** https://share.streamlit.io → select repo, branch `main`, file `app.py`, add secrets.
- **Hugging Face Spaces:** create a Space with SDK = Streamlit, push these files, add the secret in Settings.

## Secrets
Set `GEMINI_API_KEY` or `OPENAI_API_KEY`. Never commit real keys.
