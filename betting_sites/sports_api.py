import requests

def get_active_sports(api_key: str) -> list[dict]:
    url = "https://api.the-odds-api.com/v4/sports/"
    params = {
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        sports = response.json()
        active_sports = [sport for sport in sports if sport["active"] and not sport["has_outrights"]]
        
        print(f"Found {len(active_sports)} active sports/leagues")
        return active_sports
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sports list: {e}")
        return [] 