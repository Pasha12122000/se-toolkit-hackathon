import hashlib

from happiness_backend.settings import Settings


def hash_password(password: str, settings: Settings) -> str:
    return hashlib.sha256(f"{settings.auth_secret}:{password}".encode("utf-8")).hexdigest()

