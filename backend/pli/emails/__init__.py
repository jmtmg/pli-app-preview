"""Emails transactionnels — interface + impl SendGrid / Postmark / SMTP / memory."""

from .provider import EmailProvider, get_email_provider
from .sender import (
    send_invoice_email,
    send_password_reset_email,
    send_trial_reminder_email,
    send_verification_email,
)

__all__ = [
    "EmailProvider",
    "get_email_provider",
    "send_verification_email",
    "send_password_reset_email",
    "send_trial_reminder_email",
    "send_invoice_email",
]
