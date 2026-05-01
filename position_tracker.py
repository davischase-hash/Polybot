"""Dedupe trades so we only alert once per trade."""
from storage import Storage


class PositionTracker:
    def __init__(self, storage: Storage):
        self.storage = storage
        self._primed: set[str] = set()

    def filter_new(self, wallet: str, trades: list[dict]) -> list[dict]:
        """Return trades we haven't alerted on. First time we see a wallet,
        prime its history without alerting (so we don't blast old trades on startup)."""
        new = []
        priming = wallet not in self._primed

        for t in trades:
            tid = t.get("trade_id")
            if not tid:
                continue
            if self.storage.is_seen(wallet, tid):
                continue
            self.storage.mark_seen(wallet, tid)
            if not priming:
                new.append(t)

        if priming:
            self._primed.add(wallet)
        return new
