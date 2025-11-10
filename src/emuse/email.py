import datetime
import logging
import secrets
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
import pydantic
import pydantic_settings

from emuse import common, database, template

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

    # Render email templates
    template_context = {
        'first_name': first_name,
        'verification_url': verification_url,
    }

    text_content = await template.render_async(
        'email/verify.txt.j2', **template_context
    )
    html_content = await template.render_async(
        'email/verify.html.j2', **template_context
    )

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
               SET used_at = %(used_at)s
             WHERE token = %(token)s
            """,
            {'token': token, 'used_at': common.current_timestamp()},
        )

        return data['account_id']
