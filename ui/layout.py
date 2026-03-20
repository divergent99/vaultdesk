import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from config.constants import QUICK_PROMPTS

INDEX_STRING = '''<!DOCTYPE html>
<html>
<head>
    {%metas%}
    <title>VaultDesk</title>
    {%favicon%}
    {%css%}
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        html, body { height: 100%; background: #080e1e; font-family: 'DM Sans', sans-serif; }
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(201,168,76,0.4); }
        textarea { transition: border-color 0.2s, box-shadow 0.2s; }
        textarea:focus { border-color: #c9a84c !important; box-shadow: 0 0 0 3px rgba(201,168,76,0.15) !important; outline: none; }
        textarea::placeholder { color: #3d4f6e !important; }
        .qp-btn:hover { background: rgba(201,168,76,0.1) !important; border-color: rgba(201,168,76,0.3) !important; color: #e8c96d !important; }
        .send-btn:hover { background: #e8c96d !important; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(201,168,76,0.4) !important; }
        .send-btn:active { transform: translateY(0); }
        .clear-btn:hover { border-color: rgba(255,255,255,0.2) !important; color: #8899bb !important; }
        .logout-btn:hover { background: rgba(192,57,43,0.1) !important; color: #e74c3c !important; }
        #collapse-btn:hover { color: #c9a84c !important; background: rgba(201,168,76,0.08) !important; }
        #sidebar-div { contain: strict; }
        .action-chip:hover { background: rgba(201,168,76,0.1) !important; border-color: rgba(201,168,76,0.35) !important; color: #e8c96d !important; transform: translateY(-1px); }
        .copy-btn:hover { background: rgba(255,255,255,0.06) !important; color: #c9a84c !important; border-color: rgba(201,168,76,0.3) !important; }
        .copy-btn.copied { color: #3aaa6a !important; border-color: rgba(58,170,106,0.4) !important; }
        #chat-messages { justify-content: flex-start; }
        #compose-to:focus, #compose-subject:focus { border-color: #c9a84c !important; box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important; }
        #compose-body:focus { border-color: #c9a84c !important; box-shadow: 0 0 0 2px rgba(201,168,76,0.15) !important; }
        #compose-draft-btn:hover { border-color: rgba(255,255,255,0.2) !important; color: #fff !important; }
        #compose-send-btn:hover { background: #e8c96d !important; transform: translateY(-1px); }
        #compose-close:hover { color: #fff !important; background: rgba(255,255,255,0.08) !important; }
        #compose-btn:hover { color: #c9a84c !important; border-color: rgba(201,168,76,0.3) !important; background: rgba(201,168,76,0.08) !important; }
        .dot-flashing { position: relative; width: 8px; height: 8px; border-radius: 50%; background-color: #c9a84c; animation: dotFlash 1.2s infinite linear alternate; }
        .dot-flashing::before, .dot-flashing::after { content: ""; display: inline-block; position: absolute; top: 0; width: 8px; height: 8px; border-radius: 50%; background-color: #c9a84c; }
        .dot-flashing::before { left: -14px; animation: dotFlash 1.2s infinite alternate; animation-delay: -0.4s; }
        .dot-flashing::after  { left: 14px;  animation: dotFlash 1.2s infinite alternate; animation-delay: 0.4s; }
        @keyframes dotFlash { 0% { background-color: #c9a84c; } 50%, 100% { background-color: rgba(201,168,76,0.15); } }
        .login-content { animation: fadeInUp 0.6s ease forwards; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
    </style>
</head>
<body>
    {%app_entry%}
    <footer>{%config%}{%scripts%}{%renderer%}</footer>
    <script>
    document.addEventListener('click', function(e) {
        var btn = e.target.closest('.copy-btn');
        if (!btn) return;
        var text = btn.getAttribute('data-content');
        if (!text) return;
        navigator.clipboard.writeText(text).then(function() {
            var orig = btn.innerHTML;
            btn.innerHTML = '<span style="margin-right:5px">\\u2713</span>Copied!';
            btn.classList.add('copied');
            setTimeout(function() { btn.innerHTML = orig; btn.classList.remove('copied'); }, 2000);
        });
    });
    (function() {
        var search = window.location.search;
        if (search && (search.indexOf('t=') > -1 || search.indexOf('code=') > -1)) {
            var overlay = document.createElement('div');
            overlay.id = 'js-signin-overlay';
            overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:99999;background:radial-gradient(ellipse at 50% 0%, #1a2d52 0%, #080e1e 60%);display:flex;flex-direction:column;align-items:center;justify-content:center;';
            overlay.innerHTML = '<div style="width:64px;height:64px;border-radius:18px;background:linear-gradient(135deg,#c9a84c,#e8c96d);display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:800;color:#0a1020;margin-bottom:32px;font-family:DM Sans,sans-serif;box-shadow:0 8px 32px rgba(201,168,76,0.5)">DR</div><div style="color:#fff;font-size:1.15rem;font-weight:600;font-family:Plus Jakarta Sans,sans-serif;margin-bottom:12px;">Signing you in...</div><div style="color:#4a6080;font-size:0.82rem;">Securely connecting via Auth0 Token Vault</div>';
            document.body.appendChild(overlay);
            var check = setInterval(function() {
                var mainApp = document.getElementById('main-app');
                if (mainApp && mainApp.style.display !== 'none') {
                    overlay.style.opacity = '0'; overlay.style.transition = 'opacity 0.4s';
                    setTimeout(function() { overlay.remove(); }, 400);
                    clearInterval(check);
                }
            }, 200);
        }
    })();
    </script>
</body>
</html>'''


def _compose_modal():
    from config.constants import EMAIL_TEMPLATES
    return html.Div(id="compose-modal", style={"display": "none"}, children=[
        html.Div(style={
            "position": "fixed", "top": "0", "left": "0", "width": "100vw", "height": "100vh",
            "background": "rgba(0,0,0,0.7)", "zIndex": "9998",
            "display": "flex", "alignItems": "center", "justifyContent": "center",
            "backdropFilter": "blur(4px)",
        }, children=[
            html.Div(style={
                "background": "linear-gradient(135deg, #111c33 0%, #0d1628 100%)",
                "borderRadius": "20px", "padding": "32px",
                "width": "100%", "maxWidth": "560px",
                "border": "1px solid rgba(255,255,255,0.1)",
                "boxShadow": "0 24px 80px rgba(0,0,0,0.8)", "margin": "20px",
            }, children=[
                html.Div(style={"display": "flex", "justifyContent": "space-between",
                                "alignItems": "center", "marginBottom": "24px"}, children=[
                    html.Div("✍️ Compose Email", style={
                        "fontFamily": "Plus Jakarta Sans, sans-serif",
                        "fontWeight": "700", "color": "#fff", "fontSize": "1rem",
                    }),
                    html.Button("✕", id="compose-close", n_clicks=0, style={
                        "background": "transparent", "border": "none", "color": "#4a6080",
                        "fontSize": "1.1rem", "cursor": "pointer", "padding": "4px 8px",
                        "borderRadius": "6px",
                    }),
                ]),
                html.Div("TEMPLATES", style={"color": "#607898", "fontSize": "0.6rem",
                                              "fontWeight": "700", "letterSpacing": "2px",
                                              "marginBottom": "10px"}),
                html.Div(style={"display": "flex", "gap": "8px", "flexWrap": "wrap",
                                "marginBottom": "20px"}, children=[
                    html.Button(label, id={"type": "template-btn", "index": idx}, n_clicks=0,
                                style={
                                    "background": "rgba(255,255,255,0.04)",
                                    "border": "1px solid rgba(255,255,255,0.1)",
                                    "borderRadius": "20px", "padding": "6px 14px",
                                    "color": "#9ab0cc", "fontSize": "0.75rem",
                                    "cursor": "pointer", "fontFamily": "DM Sans, sans-serif",
                                    "transition": "all 0.15s",
                                })
                    for idx, (label, _, _b) in EMAIL_TEMPLATES.items()
                ]),
                html.Div("TO", style={"color": "#607898", "fontSize": "0.6rem",
                                       "fontWeight": "700", "letterSpacing": "2px",
                                       "marginBottom": "6px"}),
                dcc.Input(id="compose-to", placeholder="recipient@example.com", type="email",
                          style={"width": "100%", "background": "rgba(255,255,255,0.05)",
                                 "border": "1px solid rgba(255,255,255,0.1)",
                                 "borderRadius": "10px", "padding": "10px 14px",
                                 "color": "#fff", "fontSize": "0.85rem",
                                 "fontFamily": "DM Sans, sans-serif",
                                 "marginBottom": "14px", "outline": "none"}),
                html.Div("SUBJECT", style={"color": "#607898", "fontSize": "0.6rem",
                                            "fontWeight": "700", "letterSpacing": "2px",
                                            "marginBottom": "6px"}),
                dcc.Input(id="compose-subject", placeholder="Email subject", type="text",
                          style={"width": "100%", "background": "rgba(255,255,255,0.05)",
                                 "border": "1px solid rgba(255,255,255,0.1)",
                                 "borderRadius": "10px", "padding": "10px 14px",
                                 "color": "#fff", "fontSize": "0.85rem",
                                 "fontFamily": "DM Sans, sans-serif",
                                 "marginBottom": "14px", "outline": "none"}),
                html.Div("BODY", style={"color": "#607898", "fontSize": "0.6rem",
                                         "fontWeight": "700", "letterSpacing": "2px",
                                         "marginBottom": "6px"}),
                dcc.Textarea(id="compose-body", placeholder="Write your message here...",
                             style={"width": "100%", "background": "rgba(255,255,255,0.05)",
                                    "border": "1px solid rgba(255,255,255,0.1)",
                                    "borderRadius": "10px", "padding": "12px 14px",
                                    "color": "#fff", "fontSize": "0.85rem",
                                    "fontFamily": "DM Sans, sans-serif",
                                    "resize": "vertical", "minHeight": "140px",
                                    "outline": "none", "lineHeight": "1.6",
                                    "marginBottom": "20px"}),
                html.Div(style={"display": "flex", "gap": "10px", "justifyContent": "flex-end"},
                         children=[
                    html.Button("Save as Draft", id="compose-draft-btn", n_clicks=0, style={
                        "background": "transparent",
                        "border": "1px solid rgba(255,255,255,0.1)",
                        "color": "#9ab0cc", "padding": "10px 20px", "borderRadius": "10px",
                        "fontSize": "0.82rem", "cursor": "pointer",
                        "fontFamily": "DM Sans, sans-serif", "transition": "all 0.15s",
                    }),
                    html.Button("Send with Guardian ↑", id="compose-send-btn", n_clicks=0, style={
                        "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                        "color": "#0a1020", "border": "none", "padding": "10px 20px",
                        "borderRadius": "10px", "fontSize": "0.82rem", "fontWeight": "700",
                        "cursor": "pointer", "fontFamily": "DM Sans, sans-serif",
                        "transition": "all 0.15s",
                    }),
                ]),
            ]),
        ]),
    ])


def _sidebar():
    return html.Div(id="sidebar-div", style={
        "width": "260px", "minWidth": "260px",
        "background": "linear-gradient(180deg, #0a1020 0%, #080e1e 100%)",
        "display": "flex", "flexDirection": "column",
        "borderRight": "1px solid rgba(255,255,255,0.06)",
        "height": "100vh", "overflow": "hidden",
        "transition": "width 0.25s ease, min-width 0.25s ease",
    }, children=[
        # Logo row
        html.Div(style={"padding": "14px 0", "flexShrink": "0",
                         "borderBottom": "1px solid rgba(255,255,255,0.06)",
                         "display": "flex", "justifyContent": "center",
                         "alignItems": "center"}, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px",
                             "overflow": "hidden", "padding": "0 18px", "width": "100%"},
                     children=[
                html.Div("DR", style={
                    "width": "34px", "height": "34px", "borderRadius": "10px",
                    "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "fontSize": "0.72rem", "fontWeight": "800", "color": "#0a1020",
                    "flexShrink": "0", "fontFamily": "DM Sans, sans-serif", "letterSpacing": "0.5px",
                }),
                html.Div([html.Div("VaultDesk", style={
                    "fontFamily": "Plus Jakarta Sans, sans-serif", "fontWeight": "700",
                    "color": "#ffffff", "fontSize": "0.9rem", "lineHeight": "1.2",
                    "whiteSpace": "nowrap", "overflow": "hidden",
                })], style={"flex": "1", "overflow": "hidden", "minWidth": "0"}),
            ]),
        ]),

        html.Div(id="sidebar-content", style={
            "flex": "1", "overflowY": "auto", "padding": "0",
            "display": "flex", "flexDirection": "column", "transition": "opacity 0.2s",
        }, children=[
            html.Div(id="sidebar-user", style={"padding": "16px 18px",
                                                "borderBottom": "1px solid rgba(255,255,255,0.06)"}),

            # Capabilities
            html.Div(style={"padding": "20px 18px 8px"}, children=[
                html.Div("CAPABILITIES", style={"color": "#607898", "fontSize": "0.6rem",
                                                  "fontWeight": "700", "letterSpacing": "2px",
                                                  "marginBottom": "12px"}),
                *[html.Div(style={"display": "flex", "alignItems": "center", "gap": "10px",
                                   "padding": "7px 8px", "borderRadius": "8px"}, children=[
                    html.Span(icon, style={"fontSize": "0.85rem", "width": "20px", "textAlign": "center"}),
                    html.Span(label, style={"fontSize": "0.78rem", "color": "#9ab0cc"}),
                ]) for icon, label in [
                    ("📧", "Search & read Gmail"),
                    ("✍️", "Draft email replies"),
                    ("📤", "Send with CIBA approval"),
                    ("📅", "Check availability"),
                    ("🔍", "List upcoming meetings"),
                    ("📆", "Schedule meetings + CIBA"),
                    ("🔒", "Auth0 Token Vault"),
                    ("📲", "Guardian push approval"),
                ]],
            ]),

            # Permissions
            html.Div(style={"padding": "16px 18px 8px"}, children=[
                html.Div("PERMISSIONS", style={"color": "#607898", "fontSize": "0.6rem",
                                                "fontWeight": "700", "letterSpacing": "2px",
                                                "marginBottom": "12px"}),
                *[html.Div(style={
                    "display": "flex", "alignItems": "center", "gap": "8px",
                    "padding": "6px 8px", "borderRadius": "8px", "marginBottom": "3px",
                    "background": "rgba(58,170,106,0.05)",
                    "border": "1px solid rgba(58,170,106,0.1)",
                }, children=[
                    html.Div(style={"width": "6px", "height": "6px", "borderRadius": "50%",
                                     "background": "#3aaa6a", "flexShrink": "0",
                                     "boxShadow": "0 0 4px #3aaa6a"}),
                    html.Span(scope, style={"fontSize": "0.68rem", "color": "#6a9a7a"}),
                ]) for scope in [
                    "gmail.readonly", "gmail.compose", "gmail.send",
                    "calendar.readonly", "calendar.events",
                ]],
                html.Div(style={"marginTop": "10px", "padding": "8px 10px",
                                 "background": "rgba(201,168,76,0.05)",
                                 "border": "1px solid rgba(201,168,76,0.15)",
                                 "borderRadius": "8px", "display": "flex",
                                 "alignItems": "center", "gap": "8px"}, children=[
                    html.Span("🔒", style={"fontSize": "0.8rem"}),
                    html.Span("Managed by Auth0 Token Vault", style={
                        "fontSize": "0.65rem", "color": "#8a7040", "lineHeight": "1.4",
                    }),
                ]),
                html.Div(style={"marginTop": "6px", "padding": "8px 10px",
                                 "background": "rgba(104,144,176,0.05)",
                                 "border": "1px solid rgba(104,144,176,0.15)",
                                 "borderRadius": "8px", "display": "flex",
                                 "alignItems": "center", "gap": "8px"}, children=[
                    html.Span("📲", style={"fontSize": "0.8rem"}),
                    html.Span("CIBA push approval active", style={
                        "fontSize": "0.65rem", "color": "#6890b0", "lineHeight": "1.4",
                    }),
                ]),
            ]),

            # Quick actions
            html.Div(style={"padding": "16px 18px 8px"}, children=[
                html.Div("QUICK ACTIONS", style={"color": "#607898", "fontSize": "0.6rem",
                                                   "fontWeight": "700", "letterSpacing": "2px",
                                                   "marginBottom": "12px"}),
                *[html.Button(p, id={"type": "qp", "index": i}, n_clicks=0,
                               className="qp-btn", style={
                    "width": "100%", "textAlign": "left",
                    "background": "rgba(255,255,255,0.03)",
                    "border": "1px solid rgba(255,255,255,0.06)",
                    "color": "#9ab0cc", "padding": "9px 12px", "borderRadius": "8px",
                    "marginBottom": "5px", "fontSize": "0.76rem", "cursor": "pointer",
                    "fontFamily": "DM Sans, sans-serif", "transition": "all 0.15s",
                    "display": "block",
                }) for i, p in enumerate(QUICK_PROMPTS)],
            ]),

            html.Div(style={"flex": "1", "minHeight": "20px"}),

            # Bottom actions
            html.Div(style={"padding": "16px 18px",
                             "borderTop": "1px solid rgba(255,255,255,0.06)"}, children=[
                html.Button("🗑 Clear Chat", id="clear-btn", n_clicks=0, className="clear-btn",
                            style={
                    "width": "100%", "background": "transparent",
                    "border": "1px solid rgba(255,255,255,0.08)",
                    "color": "#5a7090", "padding": "9px", "borderRadius": "8px",
                    "marginBottom": "8px", "fontSize": "0.78rem", "cursor": "pointer",
                    "fontFamily": "DM Sans, sans-serif", "transition": "all 0.15s",
                }),
                html.A(html.Button("← Logout", className="logout-btn", style={
                    "width": "100%", "background": "transparent",
                    "border": "1px solid rgba(192,57,43,0.3)",
                    "color": "#c0403a", "padding": "9px", "borderRadius": "8px",
                    "fontSize": "0.78rem", "cursor": "pointer",
                    "fontFamily": "DM Sans, sans-serif", "transition": "all 0.15s",
                }), href="/api/logout"),
            ]),
        ]),
    ])


def _chat_panel():
    return html.Div(style={
        "flex": "1", "display": "flex", "flexDirection": "column",
        "background": "#0a1020", "overflow": "hidden", "position": "relative",
    }, children=[
        # Header bar
        html.Div(style={
            "padding": "14px 28px",
            "background": "rgba(10,16,32,0.95)",
            "borderBottom": "1px solid rgba(255,255,255,0.06)",
            "display": "flex", "justifyContent": "space-between",
            "alignItems": "center", "backdropFilter": "blur(10px)", "flexShrink": "0",
        }, children=[
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "12px"}, children=[
                html.Button("☰", id="collapse-btn", n_clicks=0, style={
                    "background": "rgba(255,255,255,0.05)",
                    "border": "1px solid rgba(255,255,255,0.08)",
                    "color": "#6890b0", "cursor": "pointer", "fontSize": "0.85rem",
                    "width": "32px", "height": "32px", "borderRadius": "8px",
                    "display": "flex", "alignItems": "center", "justifyContent": "center",
                    "transition": "all 0.15s", "flexShrink": "0", "padding": "0",
                }),
                html.Div([
                    html.Div("Email Agent", style={
                        "fontFamily": "Plus Jakarta Sans, sans-serif", "fontWeight": "700",
                        "color": "#ffffff", "fontSize": "0.95rem", "marginBottom": "2px",
                    }),
                    html.Div("Amazon Nova Lite · Auth0 Token Vault · Gmail + Calendar · CIBA",
                             style={"color": "#4a6080", "fontSize": "0.68rem",
                                    "letterSpacing": "0.3px"}),
                ]),
            ]),
            html.Div(style={"display": "flex", "alignItems": "center", "gap": "7px"}, children=[
                html.Div(id="status-dot", style={"fontSize": "0.55rem"}),
                html.Span(id="status-text", style={"color": "#6a8aaa", "fontSize": "0.72rem"}),
            ]),
        ]),

        # Messages area
        html.Div(id="chat-messages", style={
            "flex": "1", "overflowY": "auto", "padding": "24px 28px",
            "display": "flex", "flexDirection": "column",
        }, children=[]),

        # Input bar
        html.Div(style={
            "padding": "16px 28px 20px",
            "background": "rgba(8,14,30,0.98)",
            "borderTop": "1px solid rgba(255,255,255,0.05)", "flexShrink": "0",
        }, children=[
            html.Div(style={
                "display": "flex", "gap": "10px", "alignItems": "flex-end",
                "background": "rgba(255,255,255,0.03)", "borderRadius": "14px",
                "padding": "6px 6px 6px 16px",
                "border": "1px solid rgba(255,255,255,0.07)",
            }, children=[
                dcc.Textarea(
                    id="chat-input",
                    placeholder="Ask me anything about your deals, emails, or calendar...",
                    style={
                        "flex": "1", "background": "transparent", "border": "none",
                        "color": "#c8d4e8", "fontFamily": "DM Sans, sans-serif",
                        "fontSize": "0.88rem", "resize": "none", "height": "44px",
                        "outline": "none", "lineHeight": "1.55", "padding": "8px 0",
                    },
                ),
                html.Button("✍", id="compose-btn", n_clicks=0, title="Compose email", style={
                    "width": "40px", "height": "40px",
                    "background": "rgba(255,255,255,0.05)",
                    "color": "#6890b0", "border": "1px solid rgba(255,255,255,0.08)",
                    "borderRadius": "10px", "fontSize": "1rem", "cursor": "pointer",
                    "flexShrink": "0", "transition": "all 0.2s",
                }),
                html.Button("↑", id="send-btn", n_clicks=0, className="send-btn", style={
                    "width": "40px", "height": "40px",
                    "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                    "color": "#0a1020", "border": "none", "borderRadius": "10px",
                    "fontWeight": "700", "fontSize": "1.1rem", "cursor": "pointer",
                    "flexShrink": "0", "transition": "all 0.2s",
                    "boxShadow": "0 2px 10px rgba(201,168,76,0.3)",
                }),
            ]),
            html.Div(
                "VaultDesk may make mistakes. Always review drafts before sending.",
                style={"color": "#3a5070", "fontSize": "0.65rem",
                       "marginTop": "8px", "textAlign": "center"},
            ),
        ]),
    ])


def _login_screen():
    return html.Div(id="login-screen", style={"display": "block"}, children=[
        html.Div(className="login-content", style={
            "display": "flex", "flexDirection": "column", "alignItems": "center",
            "justifyContent": "center", "minHeight": "100vh",
            "background": "radial-gradient(ellipse at 50% 0%, #1a2d52 0%, #080e1e 60%)",
            "padding": "40px 20px",
        }, children=[
            html.Div("🏛️", style={
                "width": "64px", "height": "64px", "borderRadius": "18px",
                "background": "linear-gradient(135deg, #1a2d52, #0f1e3a)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "1.9rem", "marginBottom": "24px",
                "boxShadow": "0 8px 32px rgba(0,0,0,0.5)",
                "border": "1px solid rgba(201,168,76,0.25)",
            }),
            html.H1("VaultDesk", style={
                "fontFamily": "Plus Jakarta Sans, sans-serif", "fontWeight": "700",
                "color": "#fff", "fontSize": "clamp(1.4rem, 3vw, 2rem)",
                "marginBottom": "12px", "letterSpacing": "-0.5px", "textAlign": "center",
            }),
            html.P("AI-powered M&A deal assistant · Secured by Auth0 Token Vault", style={
                "color": "#6070a0", "marginBottom": "48px",
                "fontSize": "0.95rem", "textAlign": "center",
            }),
            html.A(
                html.Button("Sign in with Google", id="signin-btn", className="send-btn", style={
                    "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                    "color": "#0a1020", "border": "none", "padding": "16px 48px",
                    "borderRadius": "12px", "fontSize": "1rem", "fontWeight": "700",
                    "fontFamily": "DM Sans, sans-serif", "cursor": "pointer",
                    "boxShadow": "0 4px 20px rgba(201,168,76,0.35)",
                    "transition": "all 0.2s", "letterSpacing": "0.3px",
                }),
                href="/auth/login",
                id="signin-link",
            ),
            html.Div(style={
                "display": "flex", "gap": "24px", "marginTop": "48px",
                "flexWrap": "wrap", "justifyContent": "center",
            }, children=[
                html.Div(style={"textAlign": "center"}, children=[
                    html.Div(icon, style={"fontSize": "1.4rem", "marginBottom": "6px"}),
                    html.Div(label, style={"color": "#6070a0", "fontSize": "0.72rem"}),
                ])
                for icon, label in [("📧","Gmail"), ("📅","Calendar"), ("✍️","Drafts"), ("🔒","Token Vault")]
            ]),
        ]),
    ])


def _signing_in_screen():
    return html.Div(id="signing-in-screen", style={"display": "none"}, children=[
        html.Div(style={
            "position": "fixed", "top": "0", "left": "0", "width": "100vw", "height": "100vh",
            "zIndex": "9999",
            "background": "radial-gradient(ellipse at 50% 0%, #1a2d52 0%, #080e1e 60%)",
            "display": "flex", "flexDirection": "column",
            "alignItems": "center", "justifyContent": "center",
        }, children=[
            html.Div("DR", style={
                "width": "64px", "height": "64px", "borderRadius": "18px",
                "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                "display": "flex", "alignItems": "center", "justifyContent": "center",
                "fontSize": "1.15rem", "fontWeight": "800", "color": "#0a1020",
                "marginBottom": "32px", "fontFamily": "DM Sans, sans-serif",
                "boxShadow": "0 8px 32px rgba(201,168,76,0.5)",
            }),
            html.Div(style={"display": "flex", "alignItems": "center",
                             "gap": "16px", "marginBottom": "16px"}, children=[
                html.Div(className="dot-flashing"),
                html.Span("Signing you in...", style={
                    "color": "#ffffff", "fontSize": "1.15rem", "fontWeight": "600",
                    "fontFamily": "Plus Jakarta Sans, sans-serif", "letterSpacing": "-0.3px",
                }),
            ]),
            html.Div("Securely connecting via Auth0 Token Vault", style={
                "color": "#4a6080", "fontSize": "0.82rem",
            }),
        ]),
    ])


def create_dash_app() -> dash.Dash:
    app = dash.Dash(
        __name__,
        requests_pathname_prefix="/ui/",
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700"
            "&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap",
        ],
        suppress_callback_exceptions=True,
    )
    app.index_string = INDEX_STRING
    app.layout = html.Div(style={"height": "100vh", "background": "#080e1e", "overflow": "hidden"},
        children=[
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="session-token",    storage_type="memory"),
            dcc.Store(id="user-store",       data={}),
            dcc.Store(id="messages-store",   data=[]),
            dcc.Store(id="pending-message",  data=None),
            dcc.Store(id="sidebar-collapsed", data=False),
            dcc.Store(id="compose-open",     data=False),
            dcc.Interval(id="agent-poll", interval=1000, n_intervals=0,
                         max_intervals=1, disabled=True),
            _compose_modal(),
            _signing_in_screen(),
            _login_screen(),
            html.Div(id="main-app", style={"display": "none", "height": "100vh"}, children=[
                html.Div(style={
                    "display": "flex", "height": "100vh",
                    "fontFamily": "DM Sans, sans-serif", "overflow": "hidden",
                }, children=[
                    _sidebar(),
                    _chat_panel(),
                ]),
            ]),
        ],
    )
    return app
