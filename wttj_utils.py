import os
from dataclasses import dataclass

URL = "https://www.welcometothejungle.com/fr"


@dataclass
class Company:
    name: str
    link: str


def get_env(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {key}")
    return value
