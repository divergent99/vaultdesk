import asyncio

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from api.session_store import create_session_token, get_user_from_token
from agent.runner import run_agent, clear_conversation
from config.settings import PORT

router = APIRouter()


@router.get("/")
async def root(request: Request):
    # auth_client is attached to app.state by build_auth0()
    auth_client = request.app.state.auth_client
    try:
        from starlette.responses import Response
        response = Response()
        user = await auth_client.client.get_user(
            store_options={"request": request, "response": response}
        )
        if user:
            return RedirectResponse(url=f"/ui/?t={create_session_token(user)}")
    except Exception:
        pass
    return RedirectResponse(url="/ui/")


@router.get("/api/me")
async def api_me(token: str):
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401)
    return JSONResponse(user)


@router.post("/api/chat")
async def api_chat(request: Request):
    token = request.headers.get("X-Session-Token", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401)
    body = await request.json()
    message = body.get("message", "").strip()
    if not message:
        return JSONResponse({"error": "Empty"}, status_code=400)
    try:
        reply = await asyncio.get_event_loop().run_in_executor(
            None, run_agent, user["sub"], message
        )
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@router.get("/api/logout")
async def api_logout():
    return RedirectResponse(url=f"http://localhost:{PORT}/auth/logout")


@router.post("/api/clear")
async def api_clear(request: Request):
    token = request.headers.get("X-Session-Token", "")
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401)
    clear_conversation(user["sub"])
    return JSONResponse({"status": "cleared"})
