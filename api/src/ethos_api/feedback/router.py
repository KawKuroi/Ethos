"""Endpoint de sugerencias y contacto (D52).

Público: usable desde la landing (anónimo) y desde Ayuda (con sesión, se asocia
el usuario). Persiste siempre; el aviso por correo al admin es best-effort en
segundo plano y no bloquea la respuesta. Protegido por el rate limit por IP.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, status

from ethos_api.auth import OptionalUserId
from ethos_api.feedback.deps import RepositoryDep
from ethos_api.feedback.mailer import notify_feedback
from ethos_api.feedback.models import FeedbackInput, FeedbackRecord

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def submit_feedback(
    body: FeedbackInput,
    user_id: OptionalUserId,
    repo: RepositoryDep,
    background: BackgroundTasks,
) -> None:
    """Guarda una sugerencia o contacto y avisa al admin en segundo plano."""
    record = FeedbackRecord(
        kind=body.kind,
        message=body.message,
        category=body.category,
        name=body.name,
        email=str(body.email) if body.email else None,
        user_id=user_id,
        created_at=datetime.now(UTC),
    )
    repo.add(record)
    background.add_task(notify_feedback, record)
