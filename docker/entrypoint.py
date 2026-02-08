#!/usr/bin/env python3
import os
import sys
import yaml
from pathlib import Path

CONFIG_DIR = Path("/app/configs")
BASE_CONFIG = CONFIG_DIR / "config.yml"
DEV_CONFIG = CONFIG_DIR / "config.dev.yml"


def _as_bool(val: str) -> bool:
    if val is None:
        return None  # type: ignore
    return str(val).strip().lower() in {"1", "true", "yes", "on"}


def _as_int(val: str, default: int) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return default


def build_config_from_env(base_cfg: dict) -> dict:
    cfg = yaml.safe_load(yaml.dump(base_cfg))  # deep copy via YAML roundtrip

    # Telegram
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        cfg.setdefault("telegram", {})["token"] = token

    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if chat_id:
        cfg.setdefault("telegram", {})["chat_id"] = chat_id

    language = os.getenv("QBB_LANGUAGE")
    if language:
        cfg.setdefault("telegram", {})["language"] = language

    parse_mode = os.getenv("QBB_PARSE_MODE")
    if parse_mode:
        cfg.setdefault("telegram", {})["parse_mode"] = parse_mode

    # Logging
    log_to_file_env = os.getenv("QBB_LOG_TO_FILE")
    if log_to_file_env is not None:
        cfg.setdefault("logging", {})["log_to_file"] = _as_bool(log_to_file_env) or False

    log_level = os.getenv("QBB_LOG_LEVEL")
    if log_level:
        cfg.setdefault("logging", {})["log_level"] = log_level

    # Proxy
    proxy_enabled_env = os.getenv("QBB_PROXY_ENABLED")
    if proxy_enabled_env is not None:
        cfg.setdefault("proxy_settings", {})["proxy_enabled"] = _as_bool(proxy_enabled_env) or False

    for k_env, k_cfg in [
        ("QBB_PROXY_HOST", "proxy_host"),
        ("QBB_PROXY_PORT", "proxy_port"),
        ("QBB_PROXY_PROTOCOL", "proxy_protocol"),
        ("QBB_PROXY_USERNAME", "proxy_username"),
        ("QBB_PROXY_PASSWORD", "proxy_password"),
    ]:
        v = os.getenv(k_env)
        if v:
            cfg.setdefault("proxy_settings", {})[k_cfg] = int(v) if k_cfg == "proxy_port" else v

    return cfg


def main():
    # Make sure base config exists
    if not BASE_CONFIG.exists():
        sys.stderr.write(f"Base config not found at {BASE_CONFIG}. Exiting.\n")
        sys.exit(1)

    with BASE_CONFIG.open("r", encoding="utf-8") as f:
        base_cfg = yaml.safe_load(f)

    # If any relevant env is present, write config.dev.yml as overlay
    relevant_env = any(os.getenv(k) for k in [
        "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "QBB_LANGUAGE", "QBB_PARSE_MODE",
        "QBB_LOG_TO_FILE", "QBB_LOG_LEVEL", "QBB_PROXY_ENABLED", "QBB_PROXY_HOST",
        "QBB_PROXY_PORT", "QBB_PROXY_PROTOCOL", "QBB_PROXY_USERNAME", "QBB_PROXY_PASSWORD",
    ])

    if relevant_env:
        cfg = build_config_from_env(base_cfg)
        with DEV_CONFIG.open("w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False)
        sys.stdout.write("Rendered configs/config.dev.yml from environment variables.\n")
    else:
        sys.stdout.write("No environment overrides provided. Using existing YAML config.\n")

    # Exec the app
    os.execvp("python", ["python", "app.py"])  # replace process


if __name__ == "__main__":
    main()
