"""Soporte compartido para las entradas a mano (D51).

Las entradas a mano son `NormalizedItem` con `source="manual"` que viven en
`user_items` junto a los de proveedor: así los resúmenes, el contexto y las
tools del MCP los incluyen sin cambios. Su `external_id` lleva el prefijo
`manual:` para distinguirlas del refresco (que las conserva).
"""

from __future__ import annotations

from ethos_api.schema import NormalizedItem

MANUAL_SOURCE = "manual"
MANUAL_PREFIX = "manual:"


def is_manual(item: NormalizedItem) -> bool:
    """True si el item es una entrada a mano (no vino de un proveedor)."""
    return item.source == MANUAL_SOURCE


def manual_external_id(item: NormalizedItem) -> str:
    """`external_id` de fila de una entrada a mano (`manual:<uuid>`)."""
    return MANUAL_PREFIX + item.work.external_ids.get("manual_id", "")


def keep_manual(items: list[NormalizedItem]) -> list[NormalizedItem]:
    """Filtra las entradas a mano de una lista (para conservarlas al refrescar)."""
    return [item for item in items if is_manual(item)]
