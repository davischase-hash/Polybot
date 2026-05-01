"""SQLite persistence so we don't re-alert on startup."""
import json
import sqlite3


class Storage:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS seen_trades (wallet TEXT, trade_id TEXT, PRIMARY KEY (wallet, trade_id))"
        )
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS tracked_traders (wallet TEXT PRIMARY KEY, data TEXT)"
        )
        self.conn.commit()

    def is_seen(self, wallet: str, trade_id: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM seen_trades WHERE wallet=? AND trade_id=?", (wallet, trade_id)
        )
        return cur.fetchone() is not None

    def mark_seen(self, wallet: str, trade_id: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO seen_trades (wallet, trade_id) VALUES (?, ?)",
            (wallet, trade_id),
        )
        self.conn.commit()

    def save_tracked_traders(self, traders: list[dict]):
        self.conn.execute("DELETE FROM tracked_traders")
        for t in traders:
            self.conn.execute(
                "INSERT INTO tracked_traders (wallet, data) VALUES (?, ?)",
                (t["wallet"], json.dumps(t)),
            )
        self.conn.commit()
