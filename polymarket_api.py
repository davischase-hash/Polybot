"""Polymarket data API client. Endpoints are unofficial and may change."""
import logging
from typing import Any

import httpx

log = logging.getLogger("polymarket_api")

DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"


class PolymarketAPI:
    def __init__(self):
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self.client = httpx.AsyncClient(timeout=20.0, headers={"User-Agent": "polybot/1.0"})
        return self

    async def __aexit__(self, *exc):
        if self.client:
            await self.client.aclose()

    async def fetch_leaderboard(self, limit: int = 100) -> list[dict[str, Any]]:
        """Pull top traders by lifetime profit."""
        try:
            r = await self.client.get(
                f"{DATA_API}/leaderboard",
                params={"window": "all", "limit": limit, "orderBy": "profit"},
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "wallet": item.get("proxyWallet") or item.get("wallet"),
                    "total_pnl": float(item.get("amount", 0)),
                    "total_trades": int(item.get("trades", 0)),
                    "win_rate": float(item.get("winRate", 0)),
                    "markets_traded": int(item.get("marketsTraded", 0)),
                    "top_market_share": float(item.get("topMarketShare", 0)),
                }
                for item in data
                if item.get("proxyWallet") or item.get("wallet")
            ]
        except Exception as e:
            log.error("Leaderboard fetch failed: %s", e)
            return []

    async def fetch_recent_trades(self, wallet: str, limit: int = 20) -> list[dict[str, Any]]:
        """Get recent trades for a wallet."""
        try:
            r = await self.client.get(
                f"{DATA_API}/trades",
                params={"user": wallet, "limit": limit},
            )
            r.raise_for_status()
            data = r.json()
            return [
                {
                    "trade_id": t.get("transactionHash") or t.get("id"),
                    "timestamp": t.get("timestamp"),
                    "market": t.get("title") or t.get("market", "Unknown"),
                    "market_slug": t.get("slug"),
                    "outcome": t.get("outcome", "?"),
                    "side": t.get("side", "?"),
                    "price": float(t.get("price", 0)),
                    "size_usd": float(t.get("usdcSize", 0)),
                }
                for t in data
                if t.get("transactionHash") or t.get("id")
            ]
        except Exception as e:
            log.warning("Trades fetch failed for %s: %s", wallet[:8], e)
            return []
