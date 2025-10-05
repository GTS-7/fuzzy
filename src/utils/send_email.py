# send_email_async.py
import os
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Iterable, Optional

# --- Configuration (use env vars; avoids hardcoding secrets) ---
# SENDER_EMAIL = os.getenv("GMAIL_SENDER", "fuzzytradelogic@gmail.com")
# APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "REPLACE_ME_WITH_APP_PASSWORD")  # set env var!

SENDER_EMAIL="fuzzytradelogic@gmail.com"
APP_PASSWORD="rocqjyktyxuaryto"


async def send_email_async(
    receiver_email: str,
    subject: str,
    message_text: str,
    message_html: Optional[str] = None,
    attachments: Optional[Iterable[str]] = None,
) -> None:
    """
    Asynchronously send an email with optional attachments using Gmail + App Password.
    All blocking I/O (SMTP + file reads) is offloaded via asyncio.to_thread, so the
    event loop remains responsive.
    """

    # Build MIME message (mixed -> alternative for text/html)
    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = receiver_email

    body = MIMEMultipart("alternative")
    body.attach(MIMEText(message_text, "plain"))
    if message_html:
        body.attach(MIMEText(message_html, "html"))
    msg.attach(body)

    # Attach files (read in background threads)
    if attachments:
        for path in attachments:
            if not os.path.exists(path):
                print(f"⚠️  Attachment not found: {path}")
                continue
            try:
                data = await asyncio.to_thread(lambda p=path: open(p, "rb").read())
                part = MIMEApplication(data, Name=os.path.basename(path))
                part["Content-Disposition"] = f'attachment; filename="{os.path.basename(path)}"'
                msg.attach(part)
                print(f"📎 Attached: {os.path.basename(path)}")
            except Exception as e:
                print(f"❌ Failed attaching {path}: {e}")

    # Define blocking SMTP send
    def _send_blocking():
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())

    # Offload SMTP send to a background thread (non-blocking for the event loop)
    await asyncio.to_thread(_send_blocking)
    print(f"✅ Email sent to {receiver_email}")


def send_email_background(
    receiver_email: str,
    subject: str,
    message_text: str,
    message_html: Optional[str] = None,
    attachments: Optional[Iterable[str]] = None,
) -> None:
    """
    Fire-and-forget scheduler: queues the async send on the current event loop
    without awaiting it. Your main task continues immediately.
    """
    asyncio.create_task(
        send_email_async(
            receiver_email=receiver_email,
            subject=subject,
            message_text=message_text,
            message_html=message_html,
            attachments=attachments,
        )
    )
    print("🚀 Email task scheduled (non-blocking).")


# ----------------- Example usage -----------------
async def main():
    # Schedule (fire-and-forget) — DO NOT await it
    send_email_background(
        receiver_email="sujaygaitonde@gmail.com",
        subject="Daily Trade Report Test 📈",
        message_text="Hi,\nAttached is your daily trade report.",
        message_html="<p>Hi,<br>Attached is your <b>daily trade report</b>.</p>",
        attachments=[
            "/Users/ssg/Documents/trade/fuzzy/reports/data.csv",
            # "/absolute/path/to/data.csv",
        ],
    )

    # Your main async work continues right away:
    print("🏃 Main async task continues immediately...")

    # (Optional) simulate doing other useful work:
    await asyncio.sleep(0.1)
    print("…still doing other work while email sends in background.")


if __name__ == "__main__":
    # Safety: warn if password is still placeholder
    if APP_PASSWORD == "REPLACE_ME_WITH_APP_PASSWORD":
        print("⚠️  Set env var GMAIL_APP_PASSWORD before running.")
    asyncio.run(main())
