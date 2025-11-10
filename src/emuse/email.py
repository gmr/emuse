import datetime
import logging
import secrets
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import pydantic
import pydantic_settings

from emuse import common, database

LOGGER = logging.getLogger(__name__)


class _Settings(pydantic_settings.BaseSettings):
    model_config = {
        'case_sensitive': False,
        'env_file': '.env',
        'env_prefix': 'email_',
        'extra': 'ignore',
    }

    smtp_host: str = 'localhost'
    smtp_port: int = 587
    smtp_username: str = ''
    smtp_password: str = ''
    smtp_use_tls: bool = True
    from_address: pydantic.EmailStr = 'noreply@emuse.org'
    from_name: str = 'eMuse'
    base_url: str = 'https://emuse.org'


async def send_verification_email(
    postgres: database.ConnectionType,
    account_id: uuid.UUID,
    email: pydantic.EmailStr,
    first_name: str,
) -> None:
    """Send email verification link to the user."""
    settings = _Settings()

    # Generate secure random token
    token = secrets.token_urlsafe(32)

    # Store token in database (expires in 24 hours)
    expires_at = common.current_timestamp() + datetime.timedelta(hours=24)
    async with database.cursor(postgres) as cursor:
        await cursor.execute(
            """
            INSERT INTO v1.email_verification_tokens
                        (account_id, token, expires_at)
                 VALUES (%(account_id)s, %(token)s, %(expires_at)s)
            """,
            {
                'account_id': account_id,
                'token': token,
                'expires_at': expires_at,
            },
        )

    # Build verification URL
    verification_url = f'{settings.base_url}/verify-email/{token}'

    # Create email message
    message = MIMEMultipart('alternative')
    message['Subject'] = 'Verify your eMuse account'
    message['From'] = f'{settings.from_name} <{settings.from_address}>'
    message['To'] = str(email)

    # Plain text version
    text_content = f"""
Hello {first_name},

Thank you for signing up for eMuse! Please verify your email address
by clicking the link below:

{verification_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
The eMuse Team
"""

    # HTML version
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; \
color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Welcome to eMuse!</h2>
        <p>Hello {first_name},</p>
        <p>Thank you for signing up for eMuse! Please verify your
        email address by clicking the button below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verification_url}"
               style="background-color: #3498db; color: white; \
padding: 12px 30px;
                      text-decoration: none; border-radius: 5px; \
display: inline-block;">
                Verify Email Address
            </a>
        </div>
        <p style="color: #7f8c8d; font-size: 14px;">
            This link will expire in 24 hours.
        </p>
        <p style="color: #7f8c8d; font-size: 14px;">
            If you did not create an account, please ignore this email.
        </p>
        <hr style="border: none; border-top: 1px solid #ecf0f1; \
margin: 30px 0;">
        <p style="color: #95a5a6; font-size: 12px;">
            Best regards,<br>
            The eMuse Team
        </p>
    </div>
</body>
</html>
"""

    message.attach(MIMEText(text_content, 'plain'))
    message.attach(MIMEText(html_content, 'html'))

    # Send email
    try:
        if settings.smtp_use_tls:
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                start_tls=True,
            )
        else:
            await aiosmtplib.send(
                message,
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
            )
        LOGGER.info('Verification email sent to %s', email)
    except Exception:
        LOGGER.exception('Failed to send verification email to %s', email)
        raise


async def verify_token(
    postgres: database.ConnectionType, token: str
) -> uuid.UUID | None:
    """Verify email verification token and return account ID if valid."""
    async with database.cursor(postgres) as cursor:
        await cursor.execute(
            """
            SELECT account_id, expires_at, used_at
              FROM v1.email_verification_tokens
             WHERE token = %(token)s
            """,
            {'token': token},
        )
        if not cursor.rowcount:
            return None

        data = await cursor.fetchone()

        # Check if token has been used
        if data['used_at']:
            LOGGER.warning('Token already used: %s', token)
            return None

        # Check if token has expired
        if data['expires_at'] < common.current_timestamp():
            LOGGER.warning('Token expired: %s', token)
            return None

        # Mark token as used
        await cursor.execute(
            """
            UPDATE v1.email_verification_tokens
               SET used_at = CURRENT_TIMESTAMP
             WHERE token = %(token)s
            """,
            {'token': token},
        )

        return data['account_id']
