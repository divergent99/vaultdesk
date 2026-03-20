import base64


def extract_body(payload: dict) -> str:
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        result = extract_body(part)
        if result:
            return result
    return ""


def extract_attachments(svc, user_id: str, msg_id: str, payload: dict) -> list[str]:
    attachments = []

    def walk(part):
        filename = part.get("filename", "")
        mime = part.get("mimeType", "")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")
        size = body.get("size", 0)

        if filename and attachment_id:
            size_kb = size / 1024
            if size <= 50000 and mime in ("text/plain", "text/csv", "application/json"):
                try:
                    att = svc.users().messages().attachments().get(
                        userId=user_id, messageId=msg_id, id=attachment_id
                    ).execute()
                    content = base64.urlsafe_b64decode(att["data"] + "==").decode(
                        "utf-8", errors="ignore"
                    )
                    attachments.append(
                        f"  {filename} ({mime}, {size_kb:.1f}KB)\n" + content[:1000]
                    )
                except Exception:
                    attachments.append(
                        f"  {filename} ({mime}, {size_kb:.1f}KB) - could not read"
                    )
            else:
                attachments.append(f"  {filename} ({mime}, {size_kb:.1f}KB)")

        for sub in part.get("parts", []):
            walk(sub)

    walk(payload)
    return attachments
