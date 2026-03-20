import re
from datetime import datetime

from dash import html


# ── Markdown renderer ────────────────────────────────────────────────

def _inline_md(text):
    parts = re.split(r"(\*\*.*?\*\*|`.*?`|\*.*?\*)", text)
    result = []
    for part in parts:
        if part.startswith("**") and part.endswith("**"):
            result.append(html.Strong(part[2:-2], style={"color": "#fff", "fontWeight": "700"}))
        elif part.startswith("`") and part.endswith("`"):
            result.append(html.Code(part[1:-1], style={
                "background": "rgba(0,0,0,0.35)", "borderRadius": "4px",
                "padding": "1px 6px", "fontSize": "0.82em",
                "color": "#a8d8a8", "fontFamily": "monospace",
            }))
        elif part.startswith("*") and part.endswith("*"):
            result.append(html.Em(part[1:-1], style={"color": "#90a8c4", "fontStyle": "italic"}))
        else:
            result.append(part)
    return result if len(result) > 1 else text


def render_markdown(content: str):
    content = re.sub(r"<thinking>.*?</thinking>", "", content, flags=re.DOTALL).strip()
    lines = content.split("\n")
    elements = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            elements.append(html.Div(style={"height": "8px"}))
        elif stripped.startswith("### "):
            elements.append(html.Div(stripped[4:], style={
                "fontWeight": "700", "fontSize": "0.92rem", "color": "#f0c040",
                "marginTop": "12px", "marginBottom": "4px",
            }))
        elif stripped.startswith("## "):
            elements.append(html.Div(stripped[3:], style={
                "fontWeight": "700", "fontSize": "1rem", "color": "#ffffff",
                "marginTop": "14px", "marginBottom": "6px",
                "borderBottom": "1px solid rgba(255,255,255,0.1)", "paddingBottom": "4px",
            }))
        elif stripped.startswith("# "):
            elements.append(html.Div(stripped[2:], style={
                "fontWeight": "800", "fontSize": "1.1rem", "color": "#ffffff",
                "marginTop": "16px", "marginBottom": "8px",
            }))
        elif stripped.startswith("- ") or stripped.startswith("* "):
            elements.append(html.Div(
                style={"display": "flex", "gap": "8px", "alignItems": "flex-start",
                       "marginBottom": "4px", "paddingLeft": "4px"},
                children=[
                    html.Span("▸", style={"color": "#c9a84c", "flexShrink": "0",
                                          "marginTop": "1px", "fontSize": "0.75rem"}),
                    html.Span(_inline_md(stripped[2:]),
                              style={"color": "#c8d8ee", "lineHeight": "1.6"}),
                ],
            ))
        elif re.match(r"^\d+\.\s", stripped):
            num = re.match(r"^(\d+)\.\s", stripped).group(1)
            text = re.sub(r"^\d+\.\s", "", stripped)
            elements.append(html.Div(
                style={"display": "flex", "gap": "8px", "alignItems": "flex-start",
                       "marginBottom": "4px", "paddingLeft": "4px"},
                children=[
                    html.Span(f"{num}.", style={"color": "#c9a84c", "flexShrink": "0",
                                                "fontWeight": "600", "minWidth": "20px"}),
                    html.Span(_inline_md(text), style={"color": "#c8d8ee", "lineHeight": "1.6"}),
                ],
            ))
        elif stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            elements.append(html.Pre("\n".join(code_lines), style={
                "background": "rgba(0,0,0,0.4)", "borderRadius": "8px",
                "padding": "12px 16px", "fontSize": "0.8rem", "color": "#a8d8a8",
                "overflowX": "auto", "margin": "8px 0",
                "border": "1px solid rgba(255,255,255,0.08)", "fontFamily": "monospace",
            }))
        elif stripped.startswith("---") or stripped.startswith("==="):
            elements.append(html.Hr(style={
                "border": "none", "borderTop": "1px solid rgba(255,255,255,0.1)", "margin": "10px 0",
            }))
        elif stripped.startswith("[") and "] " in stripped:
            parts = stripped.split(" | ")
            date_part = parts[0].split("] ")[-1].strip() if parts else ""
            from_part = parts[1].strip() if len(parts) > 1 else ""
            subj_part = parts[2].strip() if len(parts) > 2 else ""
            snip_part = parts[3].strip() if len(parts) > 3 else ""
            has_att = "📎" in subj_part
            subj_clean = subj_part.replace("📎", "").strip()
            elements.append(html.Div(
                style={"background": "rgba(255,255,255,0.03)", "borderRadius": "10px",
                       "padding": "12px 14px", "marginBottom": "8px",
                       "border": "1px solid rgba(255,255,255,0.07)"},
                children=[
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between",
                               "alignItems": "flex-start", "marginBottom": "6px"},
                        children=[
                            html.Div(subj_clean or stripped, style={
                                "color": "#ffffff", "fontWeight": "600",
                                "fontSize": "0.86rem", "flex": "1", "marginRight": "8px",
                            }),
                            html.Div(
                                style={"display": "flex", "alignItems": "center",
                                       "gap": "6px", "flexShrink": "0"},
                                children=[
                                    html.Span("📎", style={"fontSize": "0.7rem"}) if has_att else None,
                                    html.Span(date_part[:16] if date_part else "", style={
                                        "color": "#4a6080", "fontSize": "0.68rem", "whiteSpace": "nowrap",
                                    }),
                                ],
                            ),
                        ],
                    ),
                    html.Div(from_part, style={
                        "color": "#6890b0", "fontSize": "0.76rem", "marginBottom": "4px",
                    }) if from_part else None,
                    html.Div(
                        snip_part[:100] + "..." if len(snip_part) > 100 else snip_part,
                        style={"color": "#3a5070", "fontSize": "0.74rem",
                               "lineHeight": "1.5", "fontStyle": "italic"},
                    ) if snip_part else None,
                ],
            ))
        else:
            elements.append(html.Div(
                _inline_md(stripped),
                style={"color": "#c8d8ee", "lineHeight": "1.7", "marginBottom": "2px"},
            ))
        i += 1
    return elements


# ── Chat bubbles ─────────────────────────────────────────────────────

def user_bubble(content: str):
    return html.Div(
        style={"display": "flex", "justifyContent": "flex-end", "marginBottom": "12px"},
        children=[
            html.Div(
                style={"display": "flex", "flexDirection": "column",
                       "alignItems": "flex-end", "maxWidth": "72%"},
                children=[
                    html.Div(content, style={
                        "background": "linear-gradient(135deg, #1e3d6e 0%, #1a3358 100%)",
                        "color": "#ffffff", "padding": "12px 18px",
                        "borderRadius": "20px 20px 4px 20px", "fontSize": "0.88rem",
                        "lineHeight": "1.65",
                        "boxShadow": "0 2px 12px rgba(0,0,0,0.3)",
                        "border": "1px solid rgba(255,255,255,0.08)",
                    }),
                ],
            )
        ],
    )


def ai_bubble(content: str):
    import uuid
    bubble_id = f"copy-{uuid.uuid4().hex[:8]}"
    clean = re.sub(r"<thinking>.*?</thinking>", "", content, flags=re.DOTALL).strip()
    return html.Div(
        style={"display": "flex", "justifyContent": "flex-start", "marginBottom": "12px"},
        children=[
            html.Div(
                style={"display": "flex", "gap": "10px", "maxWidth": "82%",
                       "alignItems": "flex-start"},
                children=[
                    html.Div("⚖", style={
                        "width": "28px", "height": "28px", "borderRadius": "50%",
                        "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "fontSize": "0.7rem", "flexShrink": "0", "marginTop": "2px",
                        "boxShadow": "0 2px 8px rgba(201,168,76,0.3)",
                    }),
                    html.Div(
                        style={
                            "background": "linear-gradient(135deg, #131f38 0%, #0f1a30 100%)",
                            "padding": "14px 18px 10px 18px",
                            "borderRadius": "4px 20px 20px 20px",
                            "border": "1px solid rgba(255,255,255,0.07)",
                            "boxShadow": "0 2px 16px rgba(0,0,0,0.4)", "flex": "1",
                        },
                        children=[
                            *render_markdown(content),
                            html.Div(
                                style={"display": "flex", "justifyContent": "flex-end",
                                       "marginTop": "10px", "paddingTop": "8px",
                                       "borderTop": "1px solid rgba(255,255,255,0.05)"},
                                children=[
                                    html.Button(
                                        [html.Span("⎘", style={"marginRight": "5px", "fontSize": "0.85rem"}), "Copy"],
                                        id={"type": "copy-btn", "id": bubble_id},
                                        n_clicks=0,
                                        **{"data-content": clean},
                                        style={
                                            "background": "transparent",
                                            "border": "1px solid rgba(255,255,255,0.08)",
                                            "color": "#4a6080", "fontSize": "0.7rem",
                                            "borderRadius": "6px", "padding": "4px 10px",
                                            "cursor": "pointer",
                                            "fontFamily": "DM Sans, sans-serif",
                                            "transition": "all 0.15s",
                                            "display": "flex", "alignItems": "center",
                                        },
                                        className="copy-btn",
                                    )
                                ],
                            ),
                        ],
                    ),
                ],
            )
        ],
    )


def thinking_bubble(msg: str = "Thinking..."):
    return html.Div(
        style={"display": "flex", "justifyContent": "flex-start", "marginBottom": "12px"},
        children=[
            html.Div(
                style={"display": "flex", "gap": "10px", "alignItems": "center"},
                children=[
                    html.Div("⚖", style={
                        "width": "28px", "height": "28px", "borderRadius": "50%",
                        "background": "linear-gradient(135deg, #c9a84c, #e8c96d)",
                        "display": "flex", "alignItems": "center", "justifyContent": "center",
                        "fontSize": "0.7rem", "flexShrink": "0",
                    }),
                    html.Div(
                        style={
                            "background": "linear-gradient(135deg, #131f38 0%, #0f1a30 100%)",
                            "padding": "14px 20px", "borderRadius": "4px 20px 20px 20px",
                            "border": "1px solid rgba(255,255,255,0.07)",
                            "display": "flex", "alignItems": "center", "gap": "12px",
                        },
                        children=[
                            html.Div(className="dot-flashing"),
                            html.Span(msg, style={
                                "color": "#7090b0", "fontSize": "0.82rem", "fontStyle": "italic",
                            }),
                        ],
                    ),
                ],
            )
        ],
    )


def action_chip(label: str, prompt: str):
    return html.Button(
        label,
        id={"type": "dash-action", "prompt": prompt},
        n_clicks=0,
        className="action-chip",
        style={
            "background": "rgba(255,255,255,0.05)",
            "border": "1px solid rgba(255,255,255,0.1)",
            "borderRadius": "20px", "padding": "9px 18px",
            "color": "#c8d8ee", "fontSize": "0.82rem",
            "cursor": "pointer", "fontFamily": "DM Sans, sans-serif",
            "transition": "all 0.18s", "whiteSpace": "nowrap",
        },
    )


def welcome_card(name: str = ""):
    hour = datetime.now().hour
    greeting = "Good Morning" if hour < 12 else "Good Afternoon" if hour < 15 else "Good Evening"
    first = name.split()[0] if name else "there"
    return html.Div(
        style={"display": "flex", "flexDirection": "column", "alignItems": "center",
               "justifyContent": "center", "flex": "1", "padding": "40px 20px",
               "textAlign": "center"},
        children=[
            html.Div(f"{greeting}, {first}.", style={
                "fontFamily": "Plus Jakarta Sans, sans-serif", "fontWeight": "800",
                "color": "#ffffff",
                "fontSize": "clamp(1.8rem, 3.5vw, 2.6rem)",
                "marginBottom": "10px", "letterSpacing": "-1px", "lineHeight": "1.15",
            }),
            html.Div("What would you like to do in your deal room today?", style={
                "color": "#4a6080", "fontSize": "1rem", "marginBottom": "48px",
            }),
            html.Div(
                style={"display": "flex", "flexWrap": "wrap", "gap": "10px",
                       "justifyContent": "center", "marginBottom": "56px", "maxWidth": "680px"},
                children=[
                    action_chip("📬 Latest emails",       "Show my latest emails"),
                    action_chip("📅 This week's meetings", "What meetings do I have this week?"),
                    action_chip("🔍 Search NDA threads",   "Search my inbox for NDA emails"),
                    action_chip("📆 Check tomorrow",       "Check my calendar for tomorrow"),
                    action_chip("🔎 Due diligence emails", "Find emails about due diligence"),
                ],
            ),
            html.Div(
                style={"display": "flex", "gap": "12px", "flexWrap": "wrap",
                       "justifyContent": "center"},
                children=[
                    html.Div(
                        style={"display": "flex", "alignItems": "center", "gap": "6px",
                               "background": "rgba(255,255,255,0.03)",
                               "border": "1px solid rgba(255,255,255,0.07)",
                               "borderRadius": "20px", "padding": "6px 14px"},
                        children=[
                            html.Div(style={"width": "6px", "height": "6px",
                                            "borderRadius": "50%", "background": dot,
                                            "boxShadow": f"0 0 6px {dot}"}),
                            html.Span(label, style={"color": "#4a6080", "fontSize": "0.72rem"}),
                        ],
                    )
                    for dot, label in [
                        ("#3aaa6a", "Gmail connected"),
                        ("#3aaa6a", "Calendar active"),
                        ("#c9a84c", "Auth0 Token Vault"),
                        ("#6890b0", "Amazon Nova Lite"),
                    ]
                ],
            ),
        ],
    )


def msg_bubble_from_store(m: dict):
    return user_bubble(m["content"]) if m["role"] == "user" else ai_bubble(m["content"])
