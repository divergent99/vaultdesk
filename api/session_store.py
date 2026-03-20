import secrets

# token -> {"name": ..., "sub": ..., "email": ...}
_token_store: dict[str, dict] = {}


def create_session_token(user: dict) -> str:
    token = secrets.token_urlsafe(32)
    _token_store[token] = {
        "name":  user.get("name", ""),
        "sub":   user.get("sub", ""),
        "email": user.get("email", ""),
    }
    return token


def get_user_from_token(token: str) -> dict | None:
    return _token_store.get(token)
