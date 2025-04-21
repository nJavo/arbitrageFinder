import requests

def get_real_odds(api_key: str, sport: str = "upcoming", regions: str = "us,eu,uk,au"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch odds for {sport} (regions: {regions}): {response.status_code} {response.text}")
        return []

    return response.json()
