"""
email_gate.py - Email gating, session usage limits, and a simple in-memory AI backstop.
"""

from __future__ import annotations

import hashlib
import re
import threading
import time

import streamlit as st


EMAIL_PATTERN = re.compile(
    r"^(?=.{6,254}$)(?P<local>[A-Za-z0-9](?:[A-Za-z0-9._%+\-]{0,62}[A-Za-z0-9])?)@"
    r"(?P<domain>(?:[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,24})$"
)

DISPOSABLE_DOMAINS = {
    "10minutemail.com",
    "20minutemail.com",
    "dispostable.com",
    "emailondeck.com",
    "fakeinbox.com",
    "getairmail.com",
    "getnada.com",
    "guerrillamail.biz",
    "guerrillamail.com",
    "guerrillamail.de",
    "guerrillamail.net",
    "guerrillamail.org",
    "maildrop.cc",
    "mailinator.com",
    "mailnesia.com",
    "mintemail.com",
    "mytemp.email",
    "sharklasers.com",
    "spambog.com",
    "temp-mail.org",
    "tempail.com",
    "tempmail.dev",
    "tempmail.email",
    "tempmailo.com",
    "throwawaymail.com",
    "trashmail.com",
    "yopmail.com",
    "yopmail.fr",
    "yopmail.net",
    "yopmail.org",
}

SUSPICIOUS_LOCALS = {
    "abc",
    "asdf",
    "demo",
    "email",
    "example",
    "hello",
    "mail",
    "sample",
    "test",
    "testing",
    "user",
}

KEYBOARD_FRAGMENTS = (
    "asdf",
    "qwer",
    "zxcv",
    "poiuy",
    "lkjh",
    "mnbv",
)

USAGE_LIMITS = {
    "form_uses": 5,
    "ai_parses": 2,
    "ai_improves": 1,
    "ai_tailors": 1,
}

GLOBAL_AI_LIMIT = 50
GLOBAL_AI_WINDOW_SECONDS = 60 * 60
_SCRAMBLED_APP_CONSTANT = "v7::resume::blueprint::gate::3129"
_GLOBAL_AI_BUCKET = {"window_started_at": time.time(), "count": 0}
_GLOBAL_AI_LOCK = threading.Lock()


def _mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[:2] + "*" * max(1, len(local) - 2)
    return f"{masked_local}@{domain}"


def _looks_random_local_part(local: str) -> bool:
    lowered = local.lower()

    if any(fragment in lowered for fragment in KEYBOARD_FRAGMENTS):
        return True

    letters_only = re.sub(r"[^a-z]", "", lowered)
    if len(letters_only) < 7:
        return False

    vowels = sum(ch in "aeiou" for ch in letters_only)
    vowel_ratio = vowels / len(letters_only)
    unique_ratio = len(set(letters_only)) / len(letters_only)
    consonant_runs = re.findall(r"[bcdfghjklmnpqrstvwxyz]{5,}", letters_only)

    return vowel_ratio < 0.22 and unique_ratio > 0.7 and bool(consonant_runs)


def validate_gate_email(email: str) -> tuple[bool, str]:
    email = email.strip().lower()
    if not email:
        return False, "Email is required."

    match = EMAIL_PATTERN.match(email)
    if not match:
        return False, "Enter a valid email address with a real domain."

    local = match.group("local")
    domain = match.group("domain")
    domain_base = domain.split(".", 1)[0]

    if domain in DISPOSABLE_DOMAINS:
        return False, "Disposable email addresses are not allowed."

    if len(local) < 6:
        return False, "Use a longer email username before the @ symbol."

    if local in SUSPICIOUS_LOCALS or (local == domain_base and local in {"abc", "test"}):
        return False, "That email looks like a placeholder. Please use a real email."

    if local == domain_base and len(set(local)) <= 4:
        return False, "That email looks synthetic. Please use a real email."

    if _looks_random_local_part(local):
        return False, "That email looks auto-generated or fake. Please use a real email."

    return True, ""


def _make_session_token(email: str, timestamp: int) -> str:
    raw = f"{email.lower()}::{timestamp}::{_SCRAMBLED_APP_CONSTANT[::-1]}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def ensure_usage_state() -> dict:
    if "email_gate_usage" not in st.session_state:
        st.session_state["email_gate_usage"] = {key: 0 for key in USAGE_LIMITS}
    return st.session_state["email_gate_usage"]


def get_usage_snapshot() -> dict:
    usage = ensure_usage_state()
    return {key: {"used": usage.get(key, 0), "limit": limit} for key, limit in USAGE_LIMITS.items()}


def check_session_limit(action: str) -> tuple[bool, str]:
    usage = ensure_usage_state()
    limit = USAGE_LIMITS.get(action)
    if limit is None:
        return False, f"Unknown usage action: {action}"

    used = usage.get(action, 0)
    if used >= limit:
        label = action.replace("_", " ")
        return False, f"Session limit reached for {label} ({limit})."

    return True, ""


def _reset_global_bucket_if_needed(now: float) -> None:
    if now - _GLOBAL_AI_BUCKET["window_started_at"] >= GLOBAL_AI_WINDOW_SECONDS:
        _GLOBAL_AI_BUCKET["window_started_at"] = now
        _GLOBAL_AI_BUCKET["count"] = 0


def check_global_ai_limit() -> tuple[bool, str]:
    now = time.time()
    with _GLOBAL_AI_LOCK:
        _reset_global_bucket_if_needed(now)
        if _GLOBAL_AI_BUCKET["count"] >= GLOBAL_AI_LIMIT:
            return False, "Global hourly AI capacity is temporarily exhausted. Please try again shortly."
    return True, ""


def check_usage_limit(action: str) -> tuple[bool, str]:
    allowed, message = check_session_limit(action)
    if not allowed:
        return allowed, message

    if action.startswith("ai_"):
        return check_global_ai_limit()

    return True, ""


def increment_usage(action: str) -> None:
    usage = ensure_usage_state()
    usage[action] = usage.get(action, 0) + 1

    if action.startswith("ai_"):
        now = time.time()
        with _GLOBAL_AI_LOCK:
            _reset_global_bucket_if_needed(now)
            _GLOBAL_AI_BUCKET["count"] += 1


def is_authenticated() -> bool:
    return bool(st.session_state.get("email_gate_authenticated") and st.session_state.get("email_gate_token"))


def render_email_gate() -> None:
    ensure_usage_state()

    if is_authenticated():
        if st.session_state.get("email_gate_show_welcome"):
            masked_email = st.session_state.get("email_gate_masked_email", "your account")
            st.success(f"Welcome, {masked_email}. You can start building now.")
            st.session_state["email_gate_show_welcome"] = False
        return

    left, center, right = st.columns([2, 3, 2])
    with center:
        st.markdown("### Continue with Email")
        st.caption("Enter a real email address to unlock the builder for this session.")

        with st.form("email_gate_form", clear_on_submit=False):
            email = st.text_input(
                "Work email",
                placeholder="you@company.com",
            )
            btn_left, btn_center, btn_right = st.columns([1, 1, 1])
            with btn_center:
                submitted = st.form_submit_button("Continue", type="primary", use_container_width=True)

    if submitted:
        valid, message = validate_gate_email(email)
        if valid:
            timestamp = int(time.time())
            st.session_state["email_gate_authenticated"] = True
            st.session_state["email_gate_token"] = _make_session_token(email, timestamp)
            st.session_state["email_gate_masked_email"] = _mask_email(email.strip().lower())
            st.session_state["email_gate_authenticated_at"] = timestamp
            st.session_state["email_gate_show_welcome"] = True
            st.session_state.pop("email_gate_error", None)
            st.rerun()
        else:
            st.session_state["email_gate_error"] = message

    if st.session_state.get("email_gate_error"):
        st.error(st.session_state["email_gate_error"])

    st.stop()
