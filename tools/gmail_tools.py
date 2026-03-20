import base64
import email.mime.text as mt

from langchain_core.tools import tool

from auth.google_token import get_google_token_sync
from auth.ciba import get_current_user, ciba_request_approval, ciba_poll_approval
from services.google_services import gmail_svc
from services.email_parser import extract_body, extract_attachments


@tool
def search_gmail(query: str, max_results: int = 8) -> str:
    """Search Gmail inbox by keyword. Returns threads with subject, sender, date, snippet."""
    try:
        svc = gmail_svc(get_google_token_sync(get_current_user()))
        res = svc.users().threads().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
        out = []
        for t in res.get("threads", []):
            d = svc.users().threads().get(
                userId="me", id=t["id"], format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            ).execute()
            h = {x["name"]: x["value"] for x in d["messages"][0]["payload"]["headers"]}
            out.append(
                f"[{t['id']}] {h.get('Date','')} | {h.get('From','')} | "
                f"{h.get('Subject','')} | {t.get('snippet','')[:100]}"
            )
        return "\n".join(out) if out else "No emails found."
    except Exception as e:
        return f"Error: {e}"


@tool
def get_latest_emails(max_results: int = 10) -> str:
    """Get the most recent emails from inbox, newest first."""
    try:
        svc = gmail_svc(get_google_token_sync(get_current_user()))
        res = svc.users().threads().list(
            userId="me", maxResults=max_results, labelIds=["INBOX"]
        ).execute()
        out = []
        for t in res.get("threads", []):
            d = svc.users().threads().get(
                userId="me", id=t["id"], format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            ).execute()
            h = {x["name"]: x["value"] for x in d["messages"][0]["payload"]["headers"]}
            has_att = any(
                p.get("filename")
                for msg in d.get("messages", [])
                for p in msg.get("payload", {}).get("parts", [])
            )
            out.append(
                f"[{t['id']}] {h.get('Date','')} | {h.get('From','')} | "
                f"{h.get('Subject','')}{'📎' if has_att else ''} | "
                f"{t.get('snippet','')[:80]}"
            )
        return "\n".join(out) if out else "No emails found."
    except Exception as e:
        return f"Error: {e}"


@tool
def read_email_thread(thread_id: str) -> str:
    """Read full content of an email thread by ID, including attachment names and content."""
    try:
        svc = gmail_svc(get_google_token_sync(get_current_user()))
        thread = svc.users().threads().get(
            userId="me", id=thread_id, format="full"
        ).execute()
        out = []
        for msg in thread.get("messages", []):
            h = {x["name"]: x["value"] for x in msg["payload"]["headers"]}
            body = extract_body(msg["payload"])
            attachments = extract_attachments(svc, "me", msg["id"], msg["payload"])
            msg_str = (
                "From: " + h.get("From", "")
                + "\nDate: " + h.get("Date", "")
                + "\n" + body[:1500]
            )
            if attachments:
                msg_str += "\n\nAttachments:\n" + "\n".join(attachments)
            out.append(msg_str)
        return "\n---\n".join(out)
    except Exception as e:
        return f"Error: {e}"


@tool
def draft_email_reply(thread_id: str, to: str, subject: str, body: str) -> str:
    """Create a DRAFT reply. Does NOT send. Returns draft ID."""
    try:
        svc = gmail_svc(get_google_token_sync(get_current_user()))
        msg = mt.MIMEText(body)
        msg["To"] = to
        msg["Subject"] = subject
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        draft = svc.users().drafts().create(
            userId="me",
            body={"message": {"threadId": thread_id, "raw": raw}},
        ).execute()
        return f"✅ Draft created (ID: {draft['id']}). Review it in Gmail before sending."
    except Exception as e:
        return f"Error: {e}"


@tool
def send_email_with_approval(thread_id: str, to: str, subject: str, body: str) -> str:
    """
    Send an email ONLY after Auth0 CIBA push notification approval on Guardian app.
    Use this DIRECTLY when user says 'send' — do NOT call draft_email_reply first.
    thread_id can be empty string "" if sending a new email not part of a thread.
    """
    try:
        import re as _re
        safe_to = _re.sub(r"[^a-zA-Z0-9]", " ", to.split("@")[0])[:20].strip()
        action_desc = f"Approve send email to {safe_to}"
        try:
            auth_req_id = ciba_request_approval(to, action_desc)
        except Exception as e:
            return f"⚠️ Could not initiate approval request: {e}"

        approved = ciba_poll_approval(auth_req_id, timeout_seconds=120)
        if not approved:
            return "❌ Email send cancelled — approval was denied or timed out on your Guardian app."

        svc = gmail_svc(get_google_token_sync(get_current_user()))
        msg = mt.MIMEText(body)
        msg["To"] = to
        msg["Subject"] = subject
        msg["References"] = thread_id
        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        svc.users().messages().send(
            userId="me",
            body={"raw": raw, "threadId": thread_id},
        ).execute()
        return f"✅ Email sent to {to} — approved via Auth0 Guardian push notification."
    except Exception as e:
        return f"Error sending email: {e}"
