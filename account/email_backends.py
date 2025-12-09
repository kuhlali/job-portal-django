from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.backends.console import EmailBackend as ConsoleBackend
from account.models import OutgoingEmail

class DBAndConsoleEmailBackend(BaseEmailBackend):
    """Email backend that records outgoing emails to the database (OutgoingEmail)
    and forwards the message to the console backend for development visibility.

    This avoids SMTP connection errors while keeping a persistent record of
    sent emails (so you can copy reset links from the DB).
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = ConsoleBackend(*args, **kwargs)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        sent_count = 0
        for message in email_messages:
            try:
                # Save to DB
                to_emails = ','.join(message.to or [])
                body = message.body or ''
                subject = message.subject or ''
                from_email = message.from_email or ''
                OutgoingEmail.objects.create(
                    subject=subject,
                    body=body,
                    to_emails=to_emails,
                    from_email=from_email,
                    sent=False,
                )
            except Exception:
                # Avoid failing send because of DB issues in dev; continue
                pass

            # Also write to console for visibility
            try:
                self.console.send_messages([message])
                sent_count += 1
            except Exception:
                # ignore console backend failures
                sent_count += 0

        return sent_count
