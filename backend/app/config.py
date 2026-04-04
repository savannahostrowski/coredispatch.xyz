from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    github_token: str = ""
    site_url: str = "http://localhost:3000"
    cors_origins: list[str] = ["http://localhost:3000"]
    editions_dir: str = str(Path(__file__).resolve().parents[2] / "editions")


settings = Settings()
