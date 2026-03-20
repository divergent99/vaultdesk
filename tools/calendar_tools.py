from datetime import datetime, timezone, timedelta

from langchain_core.tools import tool

from auth.google_token import get_google_token_sync
from auth.ciba import get_current_user, ciba_request_approval, ciba_poll_approval
from services.google_services import cal_svc


@tool
def check_calendar(date: str) -> str:
    """Check calendar availability for a date (YYYY-MM-DD). Returns busy/free slots."""
    try:
        svc = cal_svc(get_google_token_sync(get_current_user()))
        day = datetime.fromisoformat(date).replace(hour=9, minute=0, tzinfo=timezone.utc)
        end = day.replace(hour=18)
        fb = svc.freebusy().query(
            body={
                "timeMin": day.isoformat(),
                "timeMax": end.isoformat(),
                "items": [{"id": "primary"}],
            }
        ).execute()
        busy = fb.get("calendars", {}).get("primary", {}).get("busy", [])
        if not busy:
            return f"✅ Fully free on {date} (9am–6pm UTC)"
        return f"Busy on {date}:\n" + "\n".join(
            [f"  {b['start']} → {b['end']}" for b in busy]
        )
    except Exception as e:
        return f"Error: {e}"


@tool
def list_upcoming_events(days: int = 7) -> str:
    """List upcoming calendar events for the next N days."""
    try:
        svc = cal_svc(get_google_token_sync(get_current_user()))
        now = datetime.now(timezone.utc)
        res = svc.events().list(
            calendarId="primary",
            timeMin=now.isoformat(),
            timeMax=(now + timedelta(days=days)).isoformat(),
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        ).execute()
        events = res.get("items", [])
        if not events:
            return f"No events in the next {days} days."

        def fmt_attendees(event):
            attendees = [
                a["email"]
                for a in event.get("attendees", [])
                if not a.get("self", False)
            ]
            return ", ".join(attendees) if attendees else "No other attendees"

        return "\n".join([
            f"📅 {e['start'].get('dateTime', e['start'].get('date'))} | "
            f"{e.get('summary','No title')} | {fmt_attendees(e)}"
            for e in events
        ])
    except Exception as e:
        return f"Error: {e}"


@tool
def create_calendar_event(
    title: str,
    date: str,
    start_time: str,
    end_time: str,
    attendees: str,
    description: str = "",
) -> str:
    """
    Create a calendar event ONLY after Auth0 CIBA Guardian push approval.
    date format: YYYY-MM-DD, start_time/end_time format: HH:MM (24hr UTC)
    attendees: comma-separated email addresses
    Use ONLY when user explicitly asks to create/schedule a meeting.
    """
    try:
        import re as _re
        safe_title = _re.sub(r"[^a-zA-Z0-9 ]", " ", title)[:30].strip()
        action_desc = f"Create meeting {safe_title}"
        try:
            auth_req_id = ciba_request_approval("", action_desc)
        except Exception as e:
            return f"Could not initiate approval request: {e}"

        approved = ciba_poll_approval(auth_req_id, timeout_seconds=120)
        if not approved:
            return "Calendar event creation cancelled — approval was denied or timed out on your Guardian app."

        svc = cal_svc(get_google_token_sync(get_current_user()))
        attendee_list = [
            {"email": e.strip()} for e in attendees.split(",") if e.strip()
        ]
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": f"{date}T{start_time}:00Z", "timeZone": "UTC"},
            "end":   {"dateTime": f"{date}T{end_time}:00Z",   "timeZone": "UTC"},
            "attendees": attendee_list,
        }
        created = svc.events().insert(
            calendarId="primary", body=event, sendUpdates="all"
        ).execute()
        return (
            f"Calendar event created: {created.get('summary')} on {date} "
            f"from {start_time} to {end_time} UTC. Invites sent to {attendees}. "
            "Approved via Auth0 Guardian."
        )
    except Exception as e:
        return f"Error creating event: {e}"
