from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    app_name: str = "AI Executive Cockpit"
    snapshot_interval_seconds: int = 2
    chat_timeout_seconds: float = 8.0
    chat_max_retries: int = 2
    cors_origins: list[str] = field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
        ]
    )


settings = Settings()
