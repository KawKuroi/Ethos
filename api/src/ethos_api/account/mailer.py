"""Aviso por correo del borrado de cuenta programado (D53).

Best-effort y opcional, como el mailer de feedback: si no hay SMTP configurado
o no conocemos el correo del usuario, no hace nada (el usuario igual puede
deshacer desde Ajustes durante los 30 días). Usa la stdlib.
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage

from ethos_api.config import settings

logger = logging.getLogger("ethos.account")


def notify_deletion_scheduled(email: str | None, purge_after: datetime) -> bool:
    """Avisa al usuario de que su cuenta se borrará, con la fecha de purga."""
    if not settings.smtp_host or not email:
        return False
    try:
        message = EmailMessage()
        message["Subject"] = "Tu cuenta de Ethos se eliminará en 30 días"
        message["From"] = settings.feedback_from or settings.smtp_user
        message["To"] = email
        message.set_content(
            "Has solicitado eliminar tu cuenta de Ethos.\n\n"
            f"Se borrará de forma permanente el {purge_after.date().isoformat()}. "
            "Si cambias de idea, entra en Ethos → Ajustes → Zona de peligro y "
            "pulsa \"Deshacer\" antes de esa fecha.\n"
        )
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password.get_secret_value())
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException) as error:
        logger.warning("No se pudo avisar del borrado de cuenta: %s", error)
        return False
