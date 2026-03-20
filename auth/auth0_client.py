from auth0_fastapi.config import Auth0Config
from auth0_fastapi.auth.auth_client import AuthClient
from auth0_fastapi.server.routes import router as auth_router, register_auth_routes

from config.settings import AUTH0_DOMAIN, CLIENT_ID, CLIENT_SECRET, SECRET_KEY, PORT
from config.constants import GOOGLE_CONNECTION, GOOGLE_SCOPES


def build_auth0(app):
    """Attach Auth0 config + router to a FastAPI app. Returns (config, client)."""
    config = Auth0Config(
        domain=AUTH0_DOMAIN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        app_base_url=f"http://localhost:{PORT}",
        secret=SECRET_KEY,
        authorization_params={
            "scope": f"openid profile email offline_access {GOOGLE_SCOPES}",
            "connection": GOOGLE_CONNECTION,
            "access_type": "offline",
        },
    )
    client = AuthClient(config)
    app.state.config = config
    app.state.auth_client = client
    register_auth_routes(auth_router, config)
    app.include_router(auth_router)
    return config, client
