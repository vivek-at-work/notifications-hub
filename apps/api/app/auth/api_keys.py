from __future__ import annotations

import secrets
import string

import bcrypt

API_KEY_PREFIX = "nh_"


def generate_api_key() -> str:
    alphabet = string.ascii_letters + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(32))
    return f"{API_KEY_PREFIX}{token}"


def hash_api_key(plaintext: str) -> str:
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_api_key(plaintext: str, key_hash: str) -> bool:
    try:
        return bcrypt.checkpw(plaintext.encode("utf-8"), key_hash.encode("utf-8"))
    except ValueError:
        return False


def is_api_key_token(token: str) -> bool:
    return token.startswith(API_KEY_PREFIX)
