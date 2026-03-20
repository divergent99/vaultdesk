GOOGLE_CONNECTION = "google-oauth2"

GOOGLE_SCOPES = " ".join([
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
])

QUICK_PROMPTS = [
    "Show my latest emails",
    "What meetings do I have this week?",
    "Check my calendar for tomorrow",
    "Search inbox for NDA emails",
    "Find emails about due diligence",
]

# index -> (label, subject, body)
EMAIL_TEMPLATES = {
    0: (
        "Follow Up",
        "following up on our previous conversation regarding",
        "Hi,\n\nI wanted to follow up on our recent discussion. Could you please provide an update on the status?\n\nLooking forward to your response.\n\nBest regards,\nXander",
    ),
    1: (
        "Meeting Request",
        "Meeting Request",
        "Hi,\n\nI hope this message finds you well. I would like to schedule a meeting to discuss further details.\n\nPlease let me know your availability.\n\nBest regards,\nXander",
    ),
    2: (
        "NDA Acknowledgement",
        "Re: NDA Acknowledgement",
        "Hi,\n\nI acknowledge receipt of the NDA and confirm that I will review it promptly. I will revert with any comments or sign-off within the agreed timeline.\n\nBest regards,\nXander",
    ),
    3: (
        "Thank You",
        "Thank You",
        "Hi,\n\nThank you for your time and the information shared. I appreciate your prompt response and look forward to working with you.\n\nBest regards,\nXander",
    ),
    4: (
        "Quick Reply",
        "Re:",
        "Hi,\n\nThank you for your email. \n\nBest regards,\nXander",
    ),
}
