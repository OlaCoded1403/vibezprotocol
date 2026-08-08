# ================================================================
#  VIBEZ PROTOCOL — app/routes/contact.py
#  POST /api/contact → receive form, save to DB, email notification
# ================================================================

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db
from app.models import Inquiry
from app.schemas import InquiryCreate, MessageResponse

load_dotenv()

router         = APIRouter()
GMAIL_USER     = os.getenv("GMAIL_USER",         "vibezprotocol@gmail.com")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")


# Bind the outgoing socket to an IPv4 wildcard. Container runtimes commonly
# resolve AAAA records for smtp.gmail.com while having no IPv6 route, and the
# connect then fails with "[Errno 101] Network is unreachable" before Gmail is
# ever contacted. Binding to 0.0.0.0 keeps the socket on IPv4.
_IPV4_ANY = ("0.0.0.0", 0)

# 465 is implicit TLS, 587 is STARTTLS. Hosts that block one sometimes allow
# the other, so try both before giving up.
_ROUTES = (("smtp.gmail.com", 465, True), ("smtp.gmail.com", 587, False))


def _deliver(raw_message: str) -> str:
    """Send via the first SMTP route that works. Returns a label for logging."""
    errors = []
    for host, port, implicit_tls in _ROUTES:
        try:
            if implicit_tls:
                server = smtplib.SMTP_SSL(host, port, timeout=20, source_address=_IPV4_ANY)
            else:
                server = smtplib.SMTP(host, port, timeout=20, source_address=_IPV4_ANY)
            with server:
                if not implicit_tls:
                    server.starttls()
                server.login(GMAIL_USER, GMAIL_PASSWORD)
                server.sendmail(GMAIL_USER, GMAIL_USER, raw_message)
            return f"{host}:{port}"
        except Exception as exc:
            errors.append(f"{port}: {type(exc).__name__} {exc}")

    raise RuntimeError(
        "all SMTP routes failed -> " + " | ".join(errors)
        + " (if every route reports 'Network is unreachable', the host is "
          "blocking outbound SMTP and an HTTP email API is needed instead)"
    )


def send_email_notification(inquiry: Inquiry):
    """Sends you an email when someone submits the contact form."""
    if not GMAIL_PASSWORD:
        print("⚠️  GMAIL_APP_PASSWORD not set — skipping email. Check your .env file.")
        return

    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = f"[Vibez Protocol] New Inquiry: {inquiry.subject}"
        msg["From"]    = GMAIL_USER
        msg["To"]      = GMAIL_USER

        html = f"""
        <html>
        <body style="margin:0;padding:0;background:#060608;font-family:sans-serif;">
          <div style="max-width:560px;margin:2rem auto;background:#0e0e12;
                      border:1px solid #1e1e28;padding:2rem;">
            <p style="font-family:monospace;font-size:0.7rem;color:#00ff9d;
                      letter-spacing:0.15em;margin-bottom:1.5rem;">
              NEW INQUIRY — VIBEZ PROTOCOL
            </p>
            <table style="width:100%;border-collapse:collapse;">
              <tr><td style="padding:0.5rem 0;color:#6b6880;font-size:0.85rem;width:90px">From</td>
                  <td style="padding:0.5rem 0;color:#f0ede8;font-size:0.85rem">{inquiry.name}</td></tr>
              <tr><td style="padding:0.5rem 0;color:#6b6880;font-size:0.85rem">Email</td>
                  <td style="padding:0.5rem 0;color:#f0ede8;font-size:0.85rem">
                    <a href="mailto:{inquiry.email}" style="color:#00ff9d">{inquiry.email}</a></td></tr>
              <tr><td style="padding:0.5rem 0;color:#6b6880;font-size:0.85rem">Subject</td>
                  <td style="padding:0.5rem 0;color:#f0ede8;font-size:0.85rem">{inquiry.subject}</td></tr>
            </table>
            <hr style="border:none;border-top:1px solid #1e1e28;margin:1.5rem 0;">
            <p style="color:#6b6880;font-size:0.85rem;line-height:1.7;white-space:pre-wrap;">{inquiry.message}</p>
            <hr style="border:none;border-top:1px solid #1e1e28;margin:1.5rem 0;">
            <p style="font-family:monospace;font-size:0.65rem;color:#6b6880;">
              Received: {inquiry.created_at} · Vibez Protocol Backend
            </p>
          </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))
        route = _deliver(msg.as_string())

    except Exception as e:
        print(f"[email] send failed: {e} - inquiry still saved to DB")
        return

    # Logged outside the try: a failure to print must never be mistaken for a
    # failure to send (a cp1252 console raises on emoji and did exactly that).
    print(f"[email] notification for {inquiry.email} delivered via {route}")


@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def submit_contact(payload: InquiryCreate, db: Session = Depends(get_db)):
    """
    Receives contact form data from the frontend.
    Saves to database and sends an email notification to vibezprotocol@gmail.com.
    """
    inquiry = Inquiry(
        name    = payload.name,
        email   = payload.email,
        subject = payload.subject,
        message = payload.message,
    )
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)

    # Non-blocking — email failure won't break the response
    try:
        send_email_notification(inquiry)
    except Exception as e:
        print(f"Non-fatal email error: {e}")

    return {"message": "Message received! We'll be in touch soon."}
