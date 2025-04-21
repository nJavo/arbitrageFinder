from typing import List, Tuple, Dict

__all__ = [
    "inverse_sum",
    "is_arbitrage_multi",
    "calculate_stakes_multi",
]

def inverse_sum(odds: List[float]) -> float:
    """Return Σ(1/odds_i). Any odds <=0 are ignored."""
    return sum(1 / o for o in odds if o and o > 0)

def is_arbitrage_multi(best_odds: List[float]) -> Tuple[bool, float]:
    inv = inverse_sum(best_odds)
    margin = 1 - inv
    return margin > 0, margin

def calculate_stakes_multi(best_odds: List[float], bankroll: float) -> Dict[str, float]:
    inv = inverse_sum(best_odds)
    if inv >= 1:
        return {"stakes": [], "payout": 0.0, "profit": 0.0}

    payout = bankroll / inv
    stakes = [payout / o for o in best_odds]
    profit = payout - bankroll
    return {
        "stakes": stakes,
        "payout": payout,
        "profit": profit,
    }