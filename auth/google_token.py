import asyncio
import httpx
from config.settings import AUTH0_DOMAIN, CLIENT_ID, CLIENT_SECRET
from config.constants import GOOGLE_CONNECTION


async def get_google_token(user_id: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
            },
        )
        r.raise_for_status()
        mgmt_token = r.json()["access_token"]

        u = await client.get(
            f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}",
            headers={"Authorization": f"Bearer {mgmt_token}"},
        )
        u.raise_for_status()
        for identity in u.json().get("identities", []):
            if identity.get("connection") == GOOGLE_CONNECTION:
                return identity["access_token"]

    raise Exception("Google token not found. Logout and login again via Google.")


def get_google_token_sync(user_id: str) -> str:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(get_google_token(user_id))
    finally:
        loop.close()
