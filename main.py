import asyncio
import uvicorn

from ui.layout import create_dash_app
from ui.callbacks import register_callbacks
from api.app import create_app
from config.settings import PORT, AUTH0_DOMAIN


def build():
    # 1. Create Dash app and register all callbacks
    dash_app = create_dash_app()
    register_callbacks(dash_app)

    # 2. Create FastAPI app, mount Dash under /ui
    app = create_app(dash_app.server)
    return app


print("\n" + "=" * 60)
print("  Deal Room Agent")
print("=" * 60)
print(f"  Open:   http://localhost:{PORT}")
print(f"  Auth0:  {AUTH0_DOMAIN}")
print(f"  Model:  us.amazon.nova-lite-v1:0")
print(f"\n  Auth0 callback: http://localhost:{PORT}/auth/callback")
print("=" * 60 + "\n")


async def start():
    app = build()
    cfg = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning")
    server = uvicorn.Server(cfg)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(start())