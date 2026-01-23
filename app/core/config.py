import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_required_env(key: str) -> str:
    """Get required environment variable or raise error."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Required environment variable {key} is not set")
    return value


# Database configuration with validation
DB_NAME = get_required_env("DB_NAME")
DB_USER = get_required_env("DB_USER")
DB_PASSWORD = get_required_env("DB_PASSWORD")
DB_HOST = get_required_env("DB_HOST")
DB_PORT_STR = get_required_env("DB_PORT")

try:
    DB_PORT = int(DB_PORT_STR)
except (ValueError, TypeError) as e:
    raise ValueError(
        f"DB_PORT must be a valid integer, got: {DB_PORT_STR}"
    ) from e

# Computed database URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
