"""
rate_limiter.py - Compatibility wrapper around the email gate usage tracker.
"""

from __future__ import annotations

import streamlit as st

from utils.email_gate import check_usage_limit, get_usage_snapshot, increment_usage


ACTION_ALIASES = {
    "parses": "ai_parses",
    "improvements": "ai_improves",
    "tailors": "ai_tailors",
    "form_uses": "form_uses",
    "ai_parses": "ai_parses",
    "ai_improves": "ai_improves",
    "ai_tailors": "ai_tailors",
}


def _canonical_action(action: str) -> str:
    return ACTION_ALIASES.get(action, action)


def has_own_key() -> bool:
    provider = st.session_state.get("provider_choice", "chatgpt")
    return bool(st.session_state.get(f"manual_{provider}_key", "").strip())


def check_limit(action: str) -> tuple[bool, str]:
    canonical = _canonical_action(action)
    return check_usage_limit(canonical)


def increment(action: str) -> None:
    canonical = _canonical_action(action)
    increment_usage(canonical)


def remaining(action: str) -> int:
    canonical = _canonical_action(action)
    snapshot = get_usage_snapshot()
    row = snapshot.get(canonical, {"used": 0, "limit": 0})
    return max(0, row["limit"] - row["used"])


def render_usage_banner() -> None:
    snapshot = get_usage_snapshot()
    parses = snapshot["ai_parses"]
    improves = snapshot["ai_improves"]
    tailors = snapshot["ai_tailors"]

    st.info(
        "Session usage: "
        f"parse {parses['used']}/{parses['limit']} | "
        f"improve {improves['used']}/{improves['limit']} | "
        f"tailor {tailors['used']}/{tailors['limit']}",
        icon=None,
    )
