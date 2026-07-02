"""Cifrado de credenciales de terceros a nivel de app.

Usa Fernet (AES-128-CBC + HMAC). La llave (`ENCRYPTION_KEY`, urlsafe-base64 de
32 bytes) vive en el entorno/secret manager, nunca en el repo ni en la BD. El
texto plano solo existe en memoria al cifrar o descifrar.
"""

from __future__ import annotations

from typing import Annotated

from cryptography.fernet import Fernet
from fastapi import Depends

from ethos_api.config import settings


class TokenCipher:
    """Cifra y descifra credenciales con una llave Fernet."""

    def __init__(self, key: str) -> None:
        self._fernet = Fernet(key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self._fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self._fernet.decrypt(ciphertext.encode()).decode()


def get_cipher() -> TokenCipher:
    """Dependencia: construye el cifrador con la llave del entorno."""
    return TokenCipher(settings.encryption_key.get_secret_value())


CipherDep = Annotated[TokenCipher, Depends(get_cipher)]
