"""
ai_provider.py - Unified interface for Claude (Anthropic) and ChatGPT (OpenAI).
"""

from __future__ import annotations
import streamlit as st


class AIProvider:
    def complete(self, prompt: str, max_tokens: int = 4096) -> str:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        import anthropic
        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def name(self) -> str:
        return "Claude (Anthropic)"

    def complete(self, prompt: str, max_tokens: int = 4096) -> str:
        message = self._client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text


class ChatGPTProvider(AIProvider):
    def __init__(self, api_key: str):
        from openai import OpenAI
        self._client = OpenAI(api_key=api_key)

    @property
    def name(self) -> str:
        return "ChatGPT (OpenAI)"

    def complete(self, prompt: str, max_tokens: int = 4096) -> str:
        response = self._client.chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content


def get_provider(provider_name: str, api_key: str) -> AIProvider:
    if provider_name == "claude":
        return ClaudeProvider(api_key)
    elif provider_name == "chatgpt":
        return ChatGPTProvider(api_key)
    raise ValueError(f"Unknown provider: {provider_name!r}")


def _key_from_toml(provider_name: str) -> str:
    """Read key from .streamlit/secrets.toml — returns '' if missing."""
    try:
        secrets = st.secrets.get("api_keys", {})
        if provider_name == "claude":
            return secrets.get("ANTHROPIC_API_KEY", "")
        if provider_name == "chatgpt":
            return secrets.get("OPENAI_API_KEY", "")
    except Exception:
        pass
    return ""


def _default_provider() -> str:
    try:
        return st.secrets.get("settings", {}).get("default_provider", "chatgpt")
    except Exception:
        return "chatgpt"


def _manual_session_key(provider_name: str) -> str:
    return f"manual_{provider_name}_key"


def _manual_input_key(provider_name: str) -> str:
    return f"input_{_manual_session_key(provider_name)}"


def _resolve_active_key(provider_name: str) -> str:
    toml_key = _key_from_toml(provider_name)
    if toml_key:
        return toml_key

    manual_key = st.session_state.get(_manual_session_key(provider_name), "")
    if manual_key:
        return manual_key

    return st.session_state.get(_manual_input_key(provider_name), "")


def _is_key_compatible(provider_name: str, api_key: str) -> tuple[bool, str]:
    key = (api_key or "").strip()
    if not key:
        return False, "API key is required."

    looks_anthropic = key.startswith("sk-ant-") or "anthropic" in key.lower()
    looks_openai = key.startswith("sk-") and not key.startswith("sk-ant-")

    if provider_name == "claude":
        if not looks_anthropic:
            return False, "This does not look like an Anthropic key. Choose ChatGPT for an OpenAI key."
        return True, ""

    if looks_anthropic:
        return False, "This looks like an Anthropic key. Choose Claude for that key."
    if not looks_openai:
        return False, "This does not look like an OpenAI key. Use a key from platform.openai.com/api-keys."
    return True, ""


def _sync_provider_session(provider_name: str | None = None) -> tuple[str, str]:
    provider_choice = provider_name or st.session_state.get("provider_choice", _default_provider())
    active_key = _resolve_active_key(provider_choice).strip()

    if active_key:
        st.session_state[_manual_session_key(provider_choice)] = active_key

    return provider_choice, active_key


def has_provider_key(provider_name: str | None = None) -> bool:
    choice = provider_name or st.session_state.get("provider_choice", _default_provider())
    return bool(_resolve_active_key(choice).strip())


def commit_active_provider() -> bool:
    provider_choice, active_key = _sync_provider_session()

    ok, _ = _is_key_compatible(provider_choice, active_key)
    if not ok:
        st.session_state["committed_provider_choice"] = ""
        st.session_state["committed_provider_key"] = ""
        return False

    st.session_state["committed_provider_choice"] = provider_choice
    st.session_state["committed_provider_key"] = active_key
    return True


def get_active_provider() -> AIProvider | None:
    provider_choice = st.session_state.get(
        "committed_provider_choice",
        st.session_state.get("provider_choice", _default_provider()),
    )
    provider_choice, active_key = _sync_provider_session(provider_choice)

    if not active_key:
        return None

    ok, _ = _is_key_compatible(provider_choice, active_key)
    if not ok:
        return None

    try:
        return get_provider(provider_choice, active_key)
    except Exception:
        return None


def render_provider_selector() -> AIProvider | None:
    """
    Renders provider selection inline.
    - If the key exists in secrets.toml, no input box is shown.
    - If the key is missing, the user can paste it for the current session.
    Returns a ready-to-use provider or None.
    """
    provider_choice = st.radio(
        "Select your preferred AI",
        options=["claude", "chatgpt"],
        format_func=lambda x: "Claude (Anthropic)" if x == "claude" else "ChatGPT (OpenAI)",
        index=0 if _default_provider() == "claude" else 1,
        key="provider_choice",
        horizontal=True,
        label_visibility="collapsed",
    )
    toml_key = _key_from_toml(provider_choice)

    if toml_key:
        masked = toml_key[:8] + "..." + toml_key[-4:]
        st.success(f"Key loaded from secrets: `{masked}`")
        active_key = toml_key
    else:
        session_key = _manual_session_key(provider_choice)
        label = "Anthropic API Key" if provider_choice == "claude" else "OpenAI API Key"
        placeholder = "sk-ant-..." if provider_choice == "claude" else "sk-..."
        entered = st.text_input(
            label,
            value=st.session_state.get(session_key, ""),
            type="password",
            placeholder=placeholder,
            key=_manual_input_key(provider_choice),
        )
        st.session_state[session_key] = entered
        active_key = entered

        if not active_key:
            with st.expander("How to add a key via secrets.toml"):
                env_key = "ANTHROPIC_API_KEY" if provider_choice == "claude" else "OPENAI_API_KEY"
                st.code(f'[api_keys]\n{env_key} = "sk-..."', language="toml")
            return None

    ok, message = _is_key_compatible(provider_choice, active_key)
    if not ok:
        st.error(message)
        return None

    _sync_provider_session(provider_choice)

    try:
        provider = get_provider(provider_choice, active_key)
        if not toml_key:
            st.success(f"{provider.name} ready")
        return provider
    except Exception as e:
        st.error(f"{e}")
        return None
