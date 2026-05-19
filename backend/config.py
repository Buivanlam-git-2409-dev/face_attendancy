import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DEFAULT_DB_PATH = BASE_DIR / "db" / "database.db"


def loadEnvFile(envPath: Path) -> None:
    if not envPath.exists():
        return

    for rawLine in envPath.read_text(encoding="utf-8").splitlines():
        line = rawLine.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key:
            os.environ.setdefault(key, value)


loadEnvFile(ENV_PATH)


def resolveDatabaseUri(rawUri: str) -> str:
    if not rawUri:
        return f"sqlite:///{(BASE_DIR / 'db' / 'database.db').resolve().as_posix()}"

    sqlitePrefix = "sqlite:///"
    if rawUri.startswith(sqlitePrefix):
        rawPath = rawUri[len(sqlitePrefix):]
        if rawPath == ":memory:":
            return rawUri

        isWindowsAbsolute = len(rawPath) > 1 and rawPath[1] == ":"
        path = Path(rawPath) if isWindowsAbsolute else (BASE_DIR / rawPath)
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path.resolve().as_posix()}"

    return rawUri


def getBooleanEnv(name: str, defaultValue=False) -> bool:
    rawValue = os.getenv(name)
    if rawValue is None:
        return defaultValue
    return rawValue.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SQLALCHEMY_DATABASE_URI = resolveDatabaseUri(
        os.getenv(
            "DATABASE_URL",
            f"sqlite:///{DEFAULT_DB_PATH.as_posix()}",
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    CELERY_ENABLED = getBooleanEnv("CELERY_ENABLED", True)
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

