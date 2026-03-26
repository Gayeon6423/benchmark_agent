from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-5-mini"
    openrouter_site_url: str = "https://localhost"
    openrouter_site_name: str = "BenchmarkAgent"
    openrouter_ca_bundle: str | None = None
    openrouter_disable_ssl_verify: bool = False



def get_settings() -> Settings:
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY 환경변수가 필요합니다.")

    return Settings(
        openrouter_api_key=api_key,
        openrouter_model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip(),
        openrouter_site_url=os.getenv("OPENROUTER_SITE_URL", "https://localhost").strip(),
        openrouter_site_name=os.getenv("OPENROUTER_SITE_NAME", "BenchmarkAgent").strip(),
        openrouter_ca_bundle=os.getenv("OPENROUTER_CA_BUNDLE", "").strip() or None,
        openrouter_disable_ssl_verify=os.getenv("OPENROUTER_DISABLE_SSL_VERIFY", "").strip().lower()
        in {"1", "true", "yes"},
    )
