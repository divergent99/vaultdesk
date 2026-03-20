import json
import time
import urllib.parse
import requests as req
from config.settings import AUTH0_DOMAIN, CLIENT_ID, CLIENT_SECRET

# This is set by runner.py before each agent invocation so CIBA tools
# know which user to push the Guardian notification to.
_current_user_id: str = ""


def set_current_user(user_id: str) -> None:
    global _current_user_id
    _current_user_id = user_id


def get_current_user() -> str:
    return _current_user_id


def ciba_request_approval(user_email: str, action_description: str) -> str:
    r = req.post(
        f"https://{AUTH0_DOMAIN}/bc-authorize",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=urllib.parse.urlencode({
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "login_hint": json.dumps({
                "format": "iss_sub",
                "iss": f"https://{AUTH0_DOMAIN}/",
                "sub": _current_user_id,
            }),
            "binding_message": action_description[:64],
            "scope": "openid",
        }),
        timeout=15,
    )
    if r.status_code != 200:
        raise Exception(f"CIBA request failed: {r.text}")
    return r.json()["auth_req_id"]


def ciba_poll_approval(auth_req_id: str, timeout_seconds: int = 120) -> bool:
    deadline = time.time() + timeout_seconds
    print(f"[CIBA] Polling for approval, auth_req_id={auth_req_id[:20]}..., timeout={timeout_seconds}s")
    while time.time() < deadline:
        r = req.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=urllib.parse.urlencode({
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "urn:openid:params:grant-type:ciba",
                "auth_req_id": auth_req_id,
            }),
            timeout=15,
        )
        data = r.json()
        print(f"[CIBA] Poll response: {r.status_code} {data.get('error', 'OK')}")
        if r.status_code == 200:
            print("[CIBA] Approved!")
            return True
        error = data.get("error", "")
        if error == "authorization_pending":
            time.sleep(3)
        elif error == "slow_down":
            time.sleep(5)
        else:
            print(f"[CIBA] Failed: {data}")
            return False
    print("[CIBA] Timeout reached")
    return False
