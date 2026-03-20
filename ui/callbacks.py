import json
import re

import requests as req
from dash import Input, Output, State, callback_context, no_update, ALL
from dash import html

from config.constants import QUICK_PROMPTS, EMAIL_TEMPLATES
from config.settings import PORT
from ui.components import (
    msg_bubble_from_store,
    user_bubble,
    ai_bubble,
    thinking_bubble,
    welcome_card,
)


def register_callbacks(app):
    # ── Compose modal open/close ─────────────────────────────────────
    @app.callback(
        Output("compose-modal", "style"),
        Input("compose-btn",      "n_clicks"),
        Input("compose-close",    "n_clicks"),
        Input("compose-draft-btn","n_clicks"),
        Input("compose-send-btn", "n_clicks"),
        State("compose-modal",    "style"),
        prevent_initial_call=True,
    )
    def toggle_compose(open_clicks, close_clicks, draft_clicks, send_clicks, current_style):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
        if "compose-btn" in ctx.triggered[0]["prop_id"]:
            return {"display": "block"}
        return {"display": "none"}

    # ── Template fill ────────────────────────────────────────────────
    @app.callback(
        Output("compose-subject", "value"),
        Output("compose-body",    "value"),
        Input({"type": "template-btn", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def apply_template(clicks):
        ctx = callback_context
        if not ctx.triggered or not any(clicks):
            return no_update, no_update
        trigger = ctx.triggered[0]["prop_id"]
        try:
            idx = json.loads(trigger.split(".")[0])["index"]
            if not ctx.triggered[0]["value"]:
                return no_update, no_update
            _, subject, body = EMAIL_TEMPLATES[idx]
            return subject, body
        except Exception:
            return no_update, no_update

    # ── Compose send / draft ─────────────────────────────────────────
    @app.callback(
        Output("chat-messages",   "children",  allow_duplicate=True),
        Output("messages-store",  "data",      allow_duplicate=True),
        Output("pending-message", "data",      allow_duplicate=True),
        Output("agent-poll",      "disabled",  allow_duplicate=True),
        Output("agent-poll",      "n_intervals", allow_duplicate=True),
        Output("status-dot",      "children",  allow_duplicate=True),
        Output("status-text",     "children",  allow_duplicate=True),
        Output("compose-modal",   "style",     allow_duplicate=True),
        Input("compose-send-btn", "n_clicks"),
        Input("compose-draft-btn","n_clicks"),
        State("compose-to",       "value"),
        State("compose-subject",  "value"),
        State("compose-body",     "value"),
        State("messages-store",   "data"),
        State("session-token",    "data"),
        prevent_initial_call=True,
    )
    def handle_compose_action(send_clicks, draft_clicks, to, subject, body, messages, token):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, no_update, True, 0, no_update, no_update, no_update
        trigger   = ctx.triggered[0]["prop_id"]
        clicked_v = ctx.triggered[0]["value"]
        if not clicked_v or not to or not subject or not body:
            return no_update, no_update, no_update, True, 0, no_update, no_update, no_update

        messages = messages or []
        is_send  = "compose-send-btn" in trigger

        if is_send:
            message       = f"send an email to {to} with subject: {subject} and body: {body}"
            thinking_msg  = "⏳ Waiting for Guardian approval on your phone..."
            status        = "Awaiting Guardian..."
        else:
            message       = f"draft an email to {to} with subject: {subject} and body: {body}"
            thinking_msg  = "Thinking..."
            status        = "Thinking..."

        messages.append({"role": "user", "content": message})
        bubbles = [msg_bubble_from_store(m) for m in messages] + [thinking_bubble(thinking_msg)]
        return bubbles, messages, message, False, 0, "◌", status, {"display": "none"}

    # ── Sidebar collapse ─────────────────────────────────────────────
    @app.callback(
        Output("sidebar-div",       "style"),
        Output("sidebar-content",   "style"),
        Output("collapse-btn",      "children"),
        Output("sidebar-collapsed", "data"),
        Input("collapse-btn",       "n_clicks"),
        State("sidebar-collapsed",  "data"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(n_clicks, is_collapsed):
        base = {
            "background": "linear-gradient(180deg, #0a1020 0%, #080e1e 100%)",
            "display": "flex", "flexDirection": "column",
            "borderRight": "1px solid rgba(255,255,255,0.06)",
            "height": "100vh", "overflow": "hidden", "clipPath": "inset(0)",
            "transition": "width 0.3s cubic-bezier(0.4,0,0.2,1), min-width 0.3s cubic-bezier(0.4,0,0.2,1)",
        }
        if not is_collapsed:
            return (
                {**base, "width": "60px",  "minWidth": "60px"},
                {"flex": "1", "overflowY": "auto", "padding": "0",
                 "display": "none", "flexDirection": "column"},
                "→", True,
            )
        return (
            {**base, "width": "260px", "minWidth": "260px"},
            {"flex": "1", "overflowY": "auto", "padding": "0",
             "display": "flex", "flexDirection": "column"},
            "←", False,
        )

    # ── Session token extract from URL ───────────────────────────────
    @app.callback(
        Output("session-token", "data"),
        Output("user-store",    "data"),
        Input("url",            "search"),
        State("session-token",  "data"),
    )
    def extract_token(search, existing_token):
        token = None
        if search and "t=" in search:
            for part in search.lstrip("?").split("&"):
                if part.startswith("t="):
                    token = part[2:]
                    break
        if not token:
            token = existing_token
        if not token:
            return None, {}
        try:
            r = req.get(f"http://localhost:{PORT}/api/me?token={token}", timeout=3)
            if r.status_code == 200:
                return token, r.json()
        except Exception:
            pass
        return token, {}

    # ── Login/main screen toggle ─────────────────────────────────────
    @app.callback(
        Output("login-screen",      "style"),
        Output("main-app",          "style"),
        Output("sidebar-user",      "children"),
        Output("status-dot",        "children"),
        Output("status-text",       "children"),
        Output("signing-in-screen", "style"),
        Output("chat-messages",     "children"),
        Input("user-store",         "data"),
        Input("url",                "search"),
    )
    def toggle_screens(user, search):
        has_token_in_url = search and "t=" in search
        if not user or not user.get("sub"):
            if has_token_in_url:
                return (
                    {"display": "none"},
                    {"display": "none", "height": "100vh"},
                    html.Div(), "●", "Ready",
                    {"display": "block"},
                    no_update,
                )
            return (
                {"display": "block"},
                {"display": "none", "height": "100vh"},
                html.Div(), "●", "Ready",
                {"display": "none"},
                no_update,
            )
        name     = user.get("name", "User")
        initials = "".join([w[0].upper() for w in name.split()[:2]]) if name else "U"
        user_el  = html.Div(
            style={"display": "flex", "alignItems": "center", "gap": "10px"},
            children=[
                html.Div(initials, style={
                    "width": "34px", "height": "34px", "borderRadius": "10px",
                    "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                    "color": "#0a1020", "display": "flex", "alignItems": "center",
                    "justifyContent": "center", "fontWeight": "700",
                    "fontSize": "0.8rem", "flexShrink": "0",
                }),
                html.Div([
                    html.Div(name, style={"color": "#dce8f8", "fontWeight": "500",
                                          "fontSize": "0.8rem"}),
                    html.Div("● Token Vault active", style={"color": "#3aaa6a",
                                                             "fontSize": "0.65rem",
                                                             "marginTop": "1px"}),
                ]),
            ],
        )
        return (
            {"display": "none"},
            {"display": "block", "height": "100vh"},
            user_el, "●", "Ready",
            {"display": "none"},
            [welcome_card(user.get("name", ""))],
        )

    # ── Send message (chat input / quick prompts / action chips / clear) ──
    @app.callback(
        Output("chat-messages",   "children",    allow_duplicate=True),
        Output("messages-store",  "data",        allow_duplicate=True),
        Output("chat-input",      "value"),
        Output("pending-message", "data"),
        Output("agent-poll",      "disabled"),
        Output("agent-poll",      "n_intervals"),
        Output("status-dot",      "children",    allow_duplicate=True),
        Output("status-text",     "children",    allow_duplicate=True),
        Input("send-btn",                        "n_clicks"),
        Input({"type": "qp",          "index": ALL}, "n_clicks"),
        Input({"type": "dash-action", "prompt": ALL}, "n_clicks"),
        Input("clear-btn",                       "n_clicks"),
        State("chat-input",   "value"),
        State("messages-store", "data"),
        State("session-token",  "data"),
        prevent_initial_call=True,
    )
    def handle_send(send_clicks, qp_clicks, dash_clicks, clear_clicks,
                    input_val, messages, token):
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update, "", None, True, 0, "●", "Ready"
        trigger  = ctx.triggered[0]["prop_id"]
        messages = messages or []

        # Clear
        if "clear-btn" in trigger:
            try:
                if token:
                    req.post(
                        f"http://localhost:{PORT}/api/clear",
                        headers={"X-Session-Token": token},
                        timeout=5,
                    )
            except Exception:
                pass
            return [welcome_card()], [], "", None, True, 0, "●", "Ready"

        # Quick prompt
        if "qp" in trigger:
            try:
                idx = json.loads(trigger.split(".")[0])["index"]
                if not any(v for v in (qp_clicks or []) if v):
                    return no_update, no_update, "", None, True, 0, "●", "Ready"
                message = QUICK_PROMPTS[idx]
            except Exception:
                return no_update, no_update, "", None, True, 0, "●", "Ready"

        # Action chip
        elif "dash-action" in trigger:
            try:
                if not ctx.triggered[0]["value"]:
                    return no_update, no_update, "", None, True, 0, "●", "Ready"
                message = json.loads(trigger.split(".")[0])["prompt"]
            except Exception:
                return no_update, no_update, "", None, True, 0, "●", "Ready"

        # Normal text input
        else:
            message = (input_val or "").strip()

        if not message or not token:
            return no_update, no_update, "", None, True, 0, "●", "Ready"

        # Detect Guardian-approval actions to show the right thinking message
        msg_lower = message.lower().strip()
        is_send = (
            msg_lower in ["send", "yes", "yes send", "ok send",
                          "approve", "confirm send", "go ahead"]
            or msg_lower.endswith(" and send")
            or msg_lower.endswith(" then send")
            or msg_lower.startswith("send ")
            or "can you send"     in msg_lower
            or "please send"      in msg_lower
            or (re.search(r"send.{0,30}@", msg_lower) is not None)
            or "schedule a meeting" in msg_lower
            or "schedule a meet"    in msg_lower
            or "create a meeting"   in msg_lower
            or "book a meeting"     in msg_lower
            or "set up a meeting"   in msg_lower
            or "create an event"    in msg_lower
            or "schedule a call"    in msg_lower
            or "book a call"        in msg_lower
            or "set up a call"      in msg_lower
        )
        thinking_msg = (
            "⏳ Waiting for Guardian approval on your phone..."
            if is_send else "Thinking..."
        )
        status_text = "Awaiting Guardian..." if is_send else "Thinking..."

        messages.append({"role": "user", "content": message})
        bubbles = [msg_bubble_from_store(m) for m in messages] + [thinking_bubble(thinking_msg)]
        return bubbles, messages, "", message, False, 0, "◌", status_text

    # ── Poll for agent response ───────────────────────────────────────
    @app.callback(
        Output("chat-messages",   "children",  allow_duplicate=True),
        Output("messages-store",  "data",      allow_duplicate=True),
        Output("pending-message", "data",      allow_duplicate=True),
        Output("agent-poll",      "disabled",  allow_duplicate=True),
        Output("status-dot",      "children",  allow_duplicate=True),
        Output("status-text",     "children",  allow_duplicate=True),
        Input("agent-poll",       "n_intervals"),
        State("pending-message",  "data"),
        State("messages-store",   "data"),
        State("session-token",    "data"),
        prevent_initial_call=True,
    )
    def fetch_agent_response(n, pending_message, messages, token):
        if not pending_message or not token:
            return no_update, no_update, no_update, True, "●", "Ready"
        try:
            r = req.post(
                f"http://localhost:{PORT}/api/chat",
                json={"message": pending_message},
                headers={"X-Session-Token": token},
                timeout=180,
            )
            reply = r.json().get("reply", r.json().get("error", "Something went wrong."))
        except Exception as e:
            reply = f"⚠️ Error: {e}"
        messages = messages or []
        messages.append({"role": "assistant", "content": reply})
        bubbles = [msg_bubble_from_store(m) for m in messages]
        return bubbles, messages, None, True, "●", "Ready"

    # ── Browser-side greeting (uses local time, not server time) ─────
    app.clientside_callback(
        """
        function(data) {
            const hour = new Date().getHours();
            if (hour < 12) return 'Good Morning';
            if (hour < 15) return 'Good Afternoon';
            if (hour < 24) return 'Good Evening';
            return 'Night Owl 🦉';
        }
        """,
        Output("greeting-text", "children"),
        Input("user-store", "data"),
    )