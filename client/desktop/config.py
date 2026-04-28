import os


def _bool_env(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


API_BASE_URL = os.getenv("DESKTOP_API_BASE_URL", "http://127.0.0.1:5000")
API_VERIFY_TLS = _bool_env("DESKTOP_API_VERIFY_TLS", default=False)
WINDOW_MIN_WIDTH = 1080
WINDOW_MIN_HEIGHT = 720
