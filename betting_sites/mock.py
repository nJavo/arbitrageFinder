import random
import time


def generate_mock_event():
    teams = ["Lions", "Tigers", "Eagles", "Sharks", "Wolves", "Bears"]
    team_a = random.choice(teams)
    team_b = random.choice([t for t in teams if t != team_a])
    match_id = f"{team_a}vs{team_b}_{int(time.time())}"

    odds = {
        "Betfair": round(random.uniform(1.7, 2.5), 2),
        "Pinnacle": round(random.uniform(1.7, 2.5), 2)
    }

    return {
        "match_id": match_id,
        "team_a": team_a,
        "team_b": team_b,
        "odds": odds
    }
