"""Construcción y vista de las entradas a mano (D51)."""

from __future__ import annotations

from uuid import uuid4

from ethos_api.items.models import ManualItemInput, ManualItemOut
from ethos_api.items.support import MANUAL_SOURCE, is_manual, manual_external_id
from ethos_api.schema import NormalizedItem, Work


def build_manual_item(body: ManualItemInput) -> NormalizedItem:
    """Crea un `NormalizedItem` de fuente manual con un id propio (`manual_id`)."""
    return NormalizedItem(
        work=Work(
            title=body.title.strip(),
            creators=body.creators,
            year=body.year,
            external_ids={"manual_id": uuid4().hex},
        ),
        category=body.category,
        status=body.status,
        rating_normalized=body.rating,
        favorite=body.favorite,
        review=body.review,
        source=MANUAL_SOURCE,
        provenance={"source": MANUAL_SOURCE},
    )


def to_out(item: NormalizedItem) -> ManualItemOut:
    """Proyecta una entrada a mano a su vista para la web."""
    return ManualItemOut(
        external_id=manual_external_id(item),
        category=item.category,
        title=item.work.title,
        status=item.status,
        creators=item.work.creators,
        year=item.work.year,
        rating=item.rating_normalized,
        review=item.review,
        favorite=item.favorite,
    )


def manual_items(items: list[NormalizedItem]) -> list[ManualItemOut]:
    """Filtra y proyecta las entradas a mano de una lista de items."""
    return [to_out(item) for item in items if is_manual(item)]
