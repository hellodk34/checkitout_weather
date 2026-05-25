import os
from pathlib import Path

import tomllib
import tomli_w

CONFIG_DIR = Path.home() / ".config" / "checkitout_weather"
CONFIG_FILE = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict = {
    "api": {
        "host": "",
        "project_id": "",
        "credential_id": "",
        "private_key_path": "",
        "private_key": "",
    },
    "app": {
        "theme": "light",
    },
    "saved_cities": [],
}


def _deep_merge(base: dict, override: dict) -> dict:
    result = dict(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def load_config() -> dict:
    config = dict(DEFAULT_CONFIG)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "rb") as f:
            config = _deep_merge(config, tomllib.load(f))
    return config


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "wb") as f:
        tomli_w.dump(config, f)


def get_api_config() -> dict:
    cfg = load_config()
    return cfg.get("api", {})


def get_api_host() -> str:
    host = os.environ.get("QWEATHER_API_HOST")
    if host:
        return host
    return get_api_config().get("host", "")


def get_project_id() -> str:
    v = os.environ.get("QWEATHER_PROJECT_ID")
    if v:
        return v
    return get_api_config().get("project_id", "")


def get_credential_id() -> str:
    v = os.environ.get("QWEATHER_CREDENTIAL_ID")
    if v:
        return v
    return get_api_config().get("credential_id", "")


def read_private_key() -> str | None:
    pem = os.environ.get("QWEATHER_PRIVATE_KEY")
    if pem:
        return pem

    path = os.environ.get("QWEATHER_PRIVATE_KEY_PATH") or get_api_config().get(
        "private_key_path", ""
    )
    if path:
        try:
            with open(Path(path).expanduser()) as f:
                return f.read()
        except OSError:
            return None

    return get_api_config().get("private_key") or None


def get_saved_cities() -> list:
    cfg = load_config()
    return cfg.get("saved_cities", [])


def add_saved_city(city: dict):
    cfg = load_config()
    cities = cfg.setdefault("saved_cities", [])
    if not any(c["id"] == city["id"] for c in cities):
        cities.append(city)
    save_config(cfg)


def remove_saved_city(city_id: str):
    cfg = load_config()
    cities = cfg.get("saved_cities", [])
    cfg["saved_cities"] = [c for c in cities if c["id"] != city_id]
    save_config(cfg)
