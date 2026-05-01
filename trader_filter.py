"""Filter raw leaderboard down to consistently good traders."""


def filter_quality_traders(
    traders: list[dict],
    min_trades: int,
    min_win_rate: float,
    min_pnl: float,
    max_concentration: float,
) -> list[dict]:
    """
    Keep traders who:
    - Have a meaningful sample size (min_trades)
    - Win consistently (min_win_rate)
    - Have real profit (min_pnl)
    - Aren't one-market lottery winners (top_market_share <= max_concentration)
    """
    kept = []
    for t in traders:
        if t.get("total_trades", 0) < min_trades:
            continue
        if t.get("win_rate", 0) < min_win_rate:
            continue
        if t.get("total_pnl", 0) < min_pnl:
            continue
        if t.get("top_market_share", 1.0) > max_concentration:
            continue
        kept.append(t)
    return kept
