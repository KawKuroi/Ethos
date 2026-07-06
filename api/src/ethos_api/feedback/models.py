"""Modelos de sugerencias y contacto (D52)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field

FeedbackKind = Literal["suggestion", "contact"]


class FeedbackInput(BaseModel):
    """Entrada de una sugerencia o contacto."""

    message: str = Field(min_length=1, max_length=2000)
    kind: FeedbackKind = "suggestion"
    category: str | None = Field(default=None, max_length=60)
    name: str | None = Field(default=None, max_length=120)
    email: EmailStr | None = None


class FeedbackRecord(BaseModel):
    """Registro de feedback almacenado."""

    kind: FeedbackKind
    message: str
    category: str | None = None
    name: str | None = None
    email: str | None = None
    user_id: str | None = None
    created_at: datetime
