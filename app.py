"""
GenAI Chat App: deployable on Streamlit Community Cloud and Hugging Face Spaces.

Secrets (set ONE of these):
  - GEMINI_API_KEY  -> uses Google Gemini via its OpenAI-compatible endpoint
  - OPENAI_API_KEY  -> uses OpenAI

Lookup order: st.secrets (Streamlit Cloud / local secrets.toml)
              -> environment variables (Hugging Face Spaces / .env)
"""
import os

import streamlit as st
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()  # local development only; harmless on the cloud
except ImportError:
    pass

# ---------- Page config ----------
st.set_page_config(page_title="GenAI Chat Assistant", page_icon="🤖", layout="centered")

# ---------- Provider settings ----------
PROVIDERS = {
    "Gemini": {
        "secret": "GEMINI_API_KEY",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "default_model": "gemini-2.0-flash",
    },
    "OpenAI": {
        "secret": "OPENAI_API_KEY",
        "base_url": None,
        "default_model": "gpt-4o-mini",
    },
}


def get_secret(name: str):
    """Read a secret from st.secrets first, then environment variables."""
    try:
        value = st.secrets[name]
        if value:
            return value
    except Exception:
        pass  # no secrets file / key missing -> fall back to env
    return os.getenv(name)


def available_providers():
    return [p for p, cfg in PROVIDERS.items() if get_secret(cfg["secret"])]


# ---------- Session state ----------
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def reset_chat():
    st.session_state.messages = []


init_state()

# ---------- Sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    providers = available_providers()

    if not providers:
        st.error(
            "No API key found. Add `GEMINI_API_KEY` or `OPENAI_API_KEY` to your "
            "app secrets (Streamlit Cloud: Settings → Secrets; "
            "Hugging Face: Settings → Variables and secrets)."
        )
        st.stop()

    provider = st.selectbox("Provider", providers)
    cfg = PROVIDERS[provider]
    model = st.text_input("Model", value=cfg["default_model"])
    system_prompt = st.text_area(
        "System prompt",
        value="You are a helpful, concise AI assistant.",
        height=100,
    )
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max tokens", 100, 2000, 600, 50)
    st.button("🗑️ Clear chat", on_click=reset_chat, use_container_width=True)
    st.caption("API keys are loaded from secrets, never hard-coded.")


@st.cache_resource
def get_client(api_key: str, base_url):
    return OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)


client = get_client(get_secret(cfg["secret"]), cfg["base_url"])

# ---------- Main UI ----------
st.title("🤖 GenAI Chat Assistant")
st.caption(f"Powered by {provider} · model: `{model}`")

# Replay history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new input
if prompt := st.chat_input("Ask me anything..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            reply = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in stream
                if chunk.choices and chunk.choices[0].delta
            )
            st.session_state.messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            st.error(f"Request failed: {e}")
