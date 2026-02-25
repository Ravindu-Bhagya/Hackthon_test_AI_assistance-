import imaplib
import email
import os
from email.header import decode_header

def fetch_recent_emails(num_emails=10):
    """
    Fetch recent emails from Gmail using IMAP.
    Requires EMAIL_USER and EMAIL_PASS environment variables.
    Returns list of dicts with 'subject' and 'body'.
    """
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    
    if not user or not password:
        raise ValueError("EMAIL_USER and EMAIL_PASS environment variables must be set.")
    
    # Connect to Gmail IMAP
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("inbox")
    
    # Search for recent emails
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()[-num_emails:]  # Get last N emails
    
    emails = []
    for e_id in email_ids:
        # Fetch the email
        res, msg = mail.fetch(e_id, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # Parse the email
                msg = email.message_from_bytes(response[1])
                
                # Decode subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8")
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                else:
                    body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                
                emails.append({"subject": subject, "body": body})
    
    mail.logout()
    return emails