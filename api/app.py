from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config.settings import SECRET_KEY
from auth.auth0_client import build_auth0
from api.routes import router


def create_app(dash_server) -> FastAPI:
    """
    Build and return the FastAPI application.
    dash_server = dash_app.server  (passed in from ui/layout.py to avoid circular imports)
    """
    app = FastAPI(title="Deal Room")
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

    # Auth0 wires itself onto app.state and registers /auth/* routes
    build_auth0(app)

    # Our own API routes
    app.include_router(router)

    # Mount Dash WSGI app under /ui
    app.mount("/ui", WSGIMiddleware(dash_server))

    return app
