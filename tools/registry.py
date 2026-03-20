from tools.gmail_tools import (
    search_gmail,
    get_latest_emails,
    read_email_thread,
    draft_email_reply,
    send_email_with_approval,
)
from tools.calendar_tools import (
    check_calendar,
    list_upcoming_events,
    create_calendar_event,
)

TOOLS = [
    search_gmail,
    get_latest_emails,
    read_email_thread,
    draft_email_reply,
    send_email_with_approval,
    check_calendar,
    list_upcoming_events,
    create_calendar_event,
]
