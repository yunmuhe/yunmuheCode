import os

_ENV_SOURCES = {}


def load_env_file(env_file_path: str, override: bool = False) -> bool:
    """Load key-value pairs from a .env file into the process environment."""
    if not env_file_path or not os.path.exists(env_file_path):
        return False

    with open(env_file_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            if override or key not in os.environ:
                os.environ[key] = value
                _ENV_SOURCES[key] = ".env"
            else:
                _ENV_SOURCES.setdefault(key, "process_env")

    return True


def get_env_source(key: str) -> str:
    if key in _ENV_SOURCES:
        return _ENV_SOURCES[key]
    if key in os.environ:
        return "process_env"
    return "missing"


def set_env_source(key: str, source: str) -> None:
    _ENV_SOURCES[key] = source
