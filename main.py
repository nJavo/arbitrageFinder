import os
import threading
import time
from datetime import datetime
import tkinter as tk
from dotenv import load_dotenv

from arbitrage.engine import (
    is_arbitrage_multi,
    calculate_stakes_multi,
)
from arbitrage.history import BettingHistory
from arbitrage.ui import ArbitrageUI
from betting_sites.mock import generate_mock_event
from betting_sites.odds_api import get_real_odds
from betting_sites.sports_api import get_active_sports

load_dotenv(".local.env")
ODDS_API_KEY = os.getenv("ODDS_API_KEY")

seen_match_ids: set[str] = set()
BANKROLL = 100.0

def _record_and_display(ui: ArbitrageUI, history: BettingHistory, match_id: str,
                        match_name: str, bookmakers: list[dict]):
    home_best = max(b["price_home"] for b in bookmakers if b["price_home"])
    draw_prices = [b.get("price_draw") for b in bookmakers if b.get("price_draw")]
    draw_best = max(draw_prices) if draw_prices else None
    away_best = max(b["price_away"] for b in bookmakers if b["price_away"])

    odds_list = [home_best, away_best] if draw_best is None else [home_best, draw_best, away_best]

    arb, _ = is_arbitrage_multi(odds_list)
    stakes_info = calculate_stakes_multi(odds_list, BANKROLL) if arb else {"profit": 0.0}
    profit = round(stakes_info.get("profit", 0.0), 2)

    history.add_entry(
        match_id=match_id,
        bookmakers=bookmakers,
        is_arb=arb,
        profit=profit,
        timestamp=datetime.utcnow().isoformat(),
    )

    ui.add_any_match(match_id, match_name, home_best, away_best, arb, profit)
    if arb:
        ui.add_arbitrage(match_id, match_name, home_best, away_best, profit)

def mock_odds_loop(ui: ArbitrageUI, history: BettingHistory):
    while True:
        if not ui.is_fetching_enabled():
            time.sleep(1)
            continue
            
        event = generate_mock_event()
        match_id = event["match_id"]
        if match_id in seen_match_ids:
            time.sleep(0.5)
            continue
        seen_match_ids.add(match_id)

        team_a, team_b = event["team_a"], event["team_b"]
        site_a, site_b = event["odds"].keys()
        odds_a, odds_b = event["odds"][site_a], event["odds"][site_b]

        bookmakers = [
            {"site": site_a, "price_home": odds_a, "price_draw": None, "price_away": None},
            {"site": site_b, "price_home": None,   "price_draw": None, "price_away": odds_b},
        ]
        _record_and_display(ui, history, match_id, f"{team_a} vs {team_b}", bookmakers)
        time.sleep(0.5)


def real_odds_loop(ui: ArbitrageUI, history: BettingHistory):
    regions = "us,eu,uk,au"
    
    while True:
        # Check if UI is currently set to fetch data
        if not ui.is_fetching_enabled():
            time.sleep(1)
            continue
            
        if not ODDS_API_KEY:
            print("ODDS_API_KEY not set – exiting real odds loop")
            return
        
        active_sports = get_active_sports(ODDS_API_KEY)
        if not active_sports:
            print("No active sports found, using default list")
            sport_keys = [
                "soccer_epl",
                "soccer_germany_bundesliga",
                "soccer_spain_la_liga",
                "soccer_italy_serie_a",
                "soccer_france_ligue_one",
                "americanfootball_nfl",
                "basketball_nba",
                "baseball_mlb", 
                "icehockey_nhl"
            ]
        else:
            sport_keys = [sport["key"] for sport in active_sports]
            print(f"Using {len(sport_keys)} active sports: {', '.join(sport_keys[:5])}...")
            if len(sport_keys) > 5:
                print(f"...and {len(sport_keys) - 5} more")
        
        print("Fetching upcoming events across all sports...")
        upcoming_events = get_real_odds(ODDS_API_KEY, sport="upcoming", regions=regions)
        print(f'{len(upcoming_events)} upcoming events found')
        
        process_events(upcoming_events, ui, history)
        
        total_sport_events = 0
        for sport in sport_keys:
            if not ui.is_fetching_enabled():
                break
                
            print(f"Fetching odds for {sport}...")
            sport_events = get_real_odds(ODDS_API_KEY, sport=sport, regions=regions)
            print(f'{len(sport_events)} events found for {sport}')
            total_sport_events += len(sport_events)
            
            process_events(sport_events, ui, history)
            
            time.sleep(5)
        
        print(f"Processed a total of {len(upcoming_events) + total_sport_events} events")
        ui.update_last_api_time()
        print("Completed fetching odds. Waiting 120 seconds before next cycle...")
        time.sleep(120)

def process_events(events, ui, history):
    """Process a list of events and update the UI and history."""
    for ev in events:
        match_id = ev["id"]
        sport_title = ev.get("sport_title", "Unknown Sport")
        
        if match_id in seen_match_ids:
            continue
        seen_match_ids.add(match_id)

        team_a, team_b = ev["home_team"], ev["away_team"]
        bookmakers: list[dict] = []
        for b in ev.get("bookmakers", []):
            markets = b.get("markets", [])
            if not markets:
                continue
                
            outcomes = markets[0]["outcomes"]
            if len(outcomes) == 3:
                home, draw, away = outcomes
                bookmakers.append({
                    "site": b["title"],
                    "price_home": home["price"],
                    "price_draw": draw["price"],
                    "price_away": away["price"],
                })
            else:
                home, away = outcomes
                bookmakers.append({
                    "site": b["title"],
                    "price_home": home["price"],
                    "price_draw": None,
                    "price_away": away["price"],
                })
        
        if len(bookmakers) < 2:
            continue

        match_name = f"[{sport_title}] {team_a} vs {team_b}"
        _record_and_display(ui, history, match_id, match_name, bookmakers)

if __name__ == "__main__":
    root = tk.Tk()
    ui = ArbitrageUI(root)
    history = BettingHistory()
    
    print("Loading historical arbitrages...")
    ui.load_from_history(history.get_all())

    if ODDS_API_KEY:
        print("🟢 Using real odds (3‑way capable)")
        print("API fetching is paused. Click 'Start Fetching' to begin.")
        threading.Thread(target=real_odds_loop, args=(ui, history), daemon=True).start()
    else:
        print("🟡 No API key – mock 2‑way feed")
        print("API fetching is paused. Click 'Start Fetching' to begin.")
        threading.Thread(target=mock_odds_loop, args=(ui, history), daemon=True).start()

    root.mainloop()