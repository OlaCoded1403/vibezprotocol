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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.sendmail(GMAIL_USER, GMAIL_USER, msg.as_string())

        print(f"✅ Email notification sent for inquiry from {inquiry.email}")

    except Exception as e:
        print(f"❌ Email send failed: {e} — inquiry still saved to DB")


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
