"""Tests del cifrado de credenciales."""

from __future__ import annotations

import pytest
from cryptography.fernet import Fernet, InvalidToken

from ethos_api.security import TokenCipher


def test_roundtrip() -> None:
    cipher = TokenCipher(Fernet.generate_key().decode())
    secreto = "mi-token-personal"
    cifrado = cipher.encrypt(secreto)
    assert cifrado != secreto
    assert cipher.decrypt(cifrado) == secreto


def test_otra_llave_no_descifra() -> None:
    cifrado = TokenCipher(Fernet.generate_key().decode()).encrypt("x")
    otra = TokenCipher(Fernet.generate_key().decode())
    with pytest.raises(InvalidToken):
        otra.decrypt(cifrado)
