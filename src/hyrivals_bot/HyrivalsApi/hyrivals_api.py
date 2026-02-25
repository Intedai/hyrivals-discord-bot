import requests

class PlayerNotFound(Exception):
    pass

def get_stats(username: str, mode: str) -> dict:

    if mode.lower() not in ("duels, kitpvp"):
        raise ValueError

    resp = requests.get(f"https://api.hyrivals.gg/leaderboards/{mode}?page=1&limit=20&search={username}").json()
    players = resp["entries"]

    for player in players:
        if player["username"].lower() == username.lower():
            return player
    
    raise PlayerNotFound

def get_player_count():
    resp = requests.get(f"https://api.hyrivals.gg/server/count").json()

    return {
        "total": resp["count"],
        "hub": resp["servers"]["eu-hub-01"],
        "duels": resp["servers"]["eu-duels-01"],
        "kitpvp": resp["servers"]["eu-kitpvp-01"]
    }