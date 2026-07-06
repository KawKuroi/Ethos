"""Aviso por correo de sugerencias/contacto (D52).

Best-effort y opcional: si no hay SMTP configurado (host + destinatario), no
hace nada y el feedback queda solo persistido. Usa la stdlib (`smtplib`), sin
dependencias nuevas. Los fallos se registran, no se propagan: nunca deben
tumbar el envío del formulario.
"""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from ethos_api.config import settings
from ethos_api.feedback.models import FeedbackRecord

logger = logging.getLogger("ethos.feedback")


def _build_message(record: FeedbackRecord) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = f"[Ethos] Nueva {record.kind}"
    message["From"] = settings.feedback_from or settings.smtp_user
    message["To"] = settings.feedback_to
    if record.email:
        message["Reply-To"] = record.email
    lines = [
        f"Tipo: {record.kind}",
        f"Categoría: {record.category or '—'}",
        f"Nombre: {record.name or '—'}",
        f"Correo: {record.email or '—'}",
        f"Usuario: {record.user_id or 'anónimo'}",
        f"Fecha: {record.created_at.isoformat()}",
        "",
        record.message,
    ]
    message.set_content("\n".join(lines))
    return message


def notify_feedback(record: FeedbackRecord) -> bool:
    """Envía el aviso al admin si hay SMTP configurado; devuelve si se envió."""
    if not settings.smtp_host or not settings.feedback_to:
        return False
    try:
        message = _build_message(record)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
            smtp.starttls()
            if settings.smtp_user:
                smtp.login(settings.smtp_user, settings.smtp_password.get_secret_value())
            smtp.send_message(message)
        return True
    except (OSError, smtplib.SMTPException) as error:
        logger.warning("No se pudo enviar el aviso de feedback: %s", error)
        return False
