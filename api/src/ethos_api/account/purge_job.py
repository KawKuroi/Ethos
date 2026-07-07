"""Job de purga de cuentas vencidas (D53).

Pensado para ejecutarse programado (cron de Render/Supabase pg_cron o similar):

    python -m ethos_api.account.purge_job

Borra de forma permanente las cuentas cuyo `purge_after` ya pasó (usuario de
auth.users, que cascada al resto) y elimina su marca. Requiere `SUPABASE_URL` y
la service_role key en el entorno.
"""

from __future__ import annotations

import logging

from ethos_api.account.auth_admin import delete_auth_user
from ethos_api.account.service import purge_due_accounts
from ethos_api.supabase_rest import get_rest

logger = logging.getLogger("ethos.account")


def main() -> int:
    """Ejecuta la purga y devuelve cuántas cuentas se borraron."""
    rest = get_rest()
    if rest is None:
        logger.error("Sin Supabase configurado: no se puede purgar")
        return 0
    purged = purge_due_accounts(rest, delete_auth_user)
    logger.info("Cuentas purgadas: %d", purged)
    return purged


if __name__ == "__main__":  # pragma: no cover
    logging.basicConfig(level=logging.INFO)
    main()
