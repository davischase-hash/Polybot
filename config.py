"""Environment-based configuration. Railway injects these as env vars."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    telegram_bot_token: str
    telegram_chat_id: str
    poll_interval_seconds: int
    leaderboard_refresh_hours: int
    min_trades: int
    min_win_rate: float
    min_pnl_usd: float
    max_market_concentration: float
    db_path: str

    @classmethod
    def from_env(cls) -> "Config":
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
        if not token or not chat:
            raise SystemExit(
                "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID. "
                "Set them in Railway > Variables."
            )
        return cls(
            telegram_bot_token=token,
            telegram_chat_id=chat,
            poll_interval_seconds=int(os.environ.get("POLL_INTERVAL_SECONDS", "60")),
            leaderboard_refresh_hours=int(os.environ.get("LEADERBOARD_REFRESH_HOURS", "24")),
            min_trades=int(os.environ.get("MIN_TRADES", "50")),
            min_win_rate=float(os.environ.get("MIN_WIN_RATE", "0.60")),
            min_pnl_usd=float(os.environ.get("MIN_PNL_USD", "5000")),
            max_market_concentration=float(os.environ.get("MAX_MARKET_CONCENTRATION", "0.40")),
            db_path=os.environ.get("DB_PATH", "/tmp/bot_state.db"),
        )
