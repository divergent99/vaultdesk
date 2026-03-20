from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def gmail_svc(token: str):
    return build(
        "gmail", "v1",
        credentials=Credentials(token=token),
        cache_discovery=False,
    )


def cal_svc(token: str):
    return build(
        "calendar", "v3",
        credentials=Credentials(token=token),
        cache_discovery=False,
    )
