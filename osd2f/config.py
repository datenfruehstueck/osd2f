import os as _os
import typing as _typing

from .security import translate_environment_vars

translate_environment_vars()  # resolve secrets in env variables on import


class Config:
    DEBUG: bool = False
    TESTING: bool = False
    BIND: str = "127.0.0.1"
    PORT: int = 5000
    SECRET_KEY: _typing.Optional[str] = None
    DATA_PASSWORD: str = _os.environ.get("OSD2F_DATA_PASSWORD", "")
    ENTRY_SECRET: str = _os.environ.get("OSD2F_ENTRY_SECRET", "")
    ENTRY_DECRYPT_DISABLE: bool = (
        _os.environ.get("OSD2F_ENTRY_DECRYPT_DISABLE", "false").lower() == "true"
    )
    DB_URL = "sqlite://:memory:"

    # Allow for BIG submissions 4*16mb for
    # in-memory anonymization.
    # NOTE: protect POST endpoints with
    #       xsrf tokens to avoid memory
    #       based ddos attacks
    MAX_CONTENT_LENGTH: int = 16777216 * 4

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # If True, no front pages are being rendered (e.g., in survey mode where API-based communication is preferred)
    BLOCK_RENDERING = False

    # set Umlaute (and other ASCII-translated chars) handling for json.dumps (here: remains unchanged)
    JSON_AS_ASCII = True

    # token for survey API commmunication
    SURVEY_TOKEN = "do not use in production"


class Testing(Config):
    TESTING = True


class Development(Config):
    SESSION_COOKIE_SECURE = False
    DEBUG = True
    DB_URL = _os.environ.get("OSD2F_DB_URL", "sqlite://:memory:")
    SECRET_KEY = "do not use in production"


class Production(Config):
    DEBUG = False
    TESTING = False
    BIND = "0.0.0.0"
    PORT = 8000
    SECRET_KEY = _os.environ.get("OSD2F_SECRET")
    DB_URL = _os.environ.get("OSD2F_DB_URL", "")
    SESSION_COOKIE_SECURE = True  # required HTTPS server


class Survey(Production):
    BLOCK_RENDERING = True
    SURVEY_TOKEN = _os.environ.get("OSD2F_SURVEY_TOKEN")

    # changing Umlaute-JSON behavior herer
    # note that in the database, ASCII-translated chars are stored, though (e.g., \u00fc instaed of ü)
    # this can also be fixed by simply installing the orjson package in the venv which will cause tortoise to use
    # orjson.dumps (instead of json.dumps) which, by default, does not treat Umlaute
    JSON_AS_ASCII = False


# hypercorn
bind = "0.0.0.0:8000"
