import json
from datetime import datetime
from pathlib import Path

HISTORY_FILE = Path("data/history.json")


class BettingHistory:
    def __init__(self) -> None:
        self.history: list[dict] = []
        self._load()

    def _load(self) -> None:
        if HISTORY_FILE.exists() and HISTORY_FILE.stat().st_size > 0:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def _save(self) -> None:
        HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2)

    def add_entry(
        self,
        match_id: str,
        bookmakers: list[dict],
        is_arb: bool,
        profit: float,
        timestamp: str | None = None,
        home_team: str = "",
        away_team: str = "",
        sport: str = ""
    ) -> None:
        ts = timestamp or datetime.utcnow().isoformat()
        entry = {
            "match_id": match_id,
            "home_team": home_team,
            "away_team": away_team,
            "sport": sport,
            "bookmakers": bookmakers,
            "is_arb": is_arb,
            "profit": profit,
            "timestamp": ts,
        }
        self.history.append(entry)
        self._save()

    def get_all(self) -> list[dict]:
        return self.history
