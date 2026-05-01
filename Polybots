"""Polymarket copy-trade alert bot. Polls top traders, sends Telegram alerts."""
import asyncio
import logging
import sys
from datetime import datetime, timedelta

from config import Config
from polymarket_api import PolymarketAPI
from trader_filter import filter_quality_traders
from position_tracker import PositionTracker
from storage import Storage
from telegram_alerts import TelegramAlerter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger("bot")


async def refresh_leaderboard(api: PolymarketAPI, storage: Storage, cfg: Config):
    log.info("Refreshing leaderboard...")
    raw = await api.fetch_leaderboard()
    quality = filter_quality_traders(
        raw,
        min_trades=cfg.min_trades,
        min_win_rate=cfg.min_win_rate,
        min_pnl=cfg.min_pnl_usd,
        max_concentration=cfg.max_market_concentration,
    )
    storage.save_tracked_traders(quality)
    log.info("Tracking %d quality traders (filtered from %d)", len(quality), len(raw))
    return quality


async def main():
    cfg = Config.from_env()
    storage = Storage(cfg.db_path)
    alerter = TelegramAlerter(cfg.telegram_bot_token, cfg.telegram_chat_id)
    tracker = PositionTracker(storage)

    async with PolymarketAPI() as api:
        await alerter.send_message("🤖 Polymarket alert bot started")
        traders = await refresh_leaderboard(api, storage, cfg)
        last_refresh = datetime.utcnow()

        while True:
            try:
                if datetime.utcnow() - last_refresh > timedelta(hours=cfg.leaderboard_refresh_hours):
                    traders = await refresh_leaderboard(api, storage, cfg)
                    last_refresh = datetime.utcnow()

                for trader in traders:
                    wallet = trader["wallet"]
                    trades = await api.fetch_recent_trades(wallet)
                    new_trades = tracker.filter_new(wallet, trades)
                    for t in new_trades:
                        await alerter.send_trade_alert(wallet, t, stats=trader)

                await asyncio.sleep(cfg.poll_interval_seconds)
            except Exception as e:
                log.exception("Loop error: %s", e)
                await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
