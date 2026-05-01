"""Telegram alert sender."""
import logging

import httpx

log = logging.getLogger("telegram")


class TelegramAlerter:
    def __init__(self, token: str, chat_id: str):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    async def send_message(self, text: str):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    self.url,
                    json={
                        "chat_id": self.chat_id,
                        "text": text,
                        "parse_mode": "Markdown",
                        "disable_web_page_preview": True,
                    },
                )
                r.raise_for_status()
        except Exception as e:
            log.error("Telegram send failed: %s", e)

    async def send_trade_alert(self, wallet: str, trade: dict, stats: dict | None = None):
        side = trade.get("side", "?").upper()
        outcome = trade.get("outcome", "?")
        price = trade.get("price", 0)
        size = trade.get("size_usd", 0)
        market = trade.get("market", "Unknown")
        slug = trade.get("market_slug")

        emoji = "🟢" if side == "BUY" else "🔴"
        market_link = (
            f"https://polymarket.com/event/{slug}" if slug else "https://polymarket.com"
        )
        wallet_short = f"`{wallet[:6]}...{wallet[-4:]}`"

        stats_line = ""
        if stats:
            stats_line = (
                f"\n_Trader: {stats.get('win_rate', 0):.0%} win rate over "
                f"{stats.get('total_trades', 0)} trades, "
                f"${stats.get('total_pnl', 0):,.0f} P&L_"
            )

        msg = (
            f"{emoji} *{side} {outcome}* @ {price:.2f}\n"
            f"*Market:* [{market}]({market_link})\n"
            f"*Size:* ${size:,.0f}\n"
            f"*Wallet:* {wallet_short}"
            f"{stats_line}"
        )
        await self.send_message(msg)
