import os

from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = "ForgeMath"
SERVICE_VERSION = "0.1.0"
DATABASE_URL = os.getenv("FORGEMATH_DATABASE_URL", "sqlite:///./forgemath.db")
HOST = os.getenv("FORGEMATH_HOST", "127.0.0.1")
PORT = int(os.getenv("FORGEMATH_PORT", "8011"))


def validate_config() -> None:
    if not DATABASE_URL.strip():
        raise ValueError("FORGEMATH_DATABASE_URL must not be empty.")
    if not HOST.strip():
        raise ValueError("FORGEMATH_HOST must not be empty.")
    if PORT < 1 or PORT > 65535:
        raise ValueError("FORGEMATH_PORT must be between 1 and 65535.")

