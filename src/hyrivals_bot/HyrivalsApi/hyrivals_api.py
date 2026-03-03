import requests

class PlayerNotFound(Exception):
    pass

def get_duels_classes() -> dict:
    return requests.get("https://api.hyrivals.gg/leaderboards/duels?page=1&limit=1").json()["classes"]

def get_leaderboard(page: int, limit: int, mode: str, duel_class: str | None = None) -> dict:

    if mode.lower() not in ("duels, kitpvp"):
        raise ValueError(f"Mode must be duels or kitpvp, mode is {mode}")
    elif mode.lower() != "duels" and duel_class:
        raise ValueError(f"Mode must be duels or kitpvp, mode is {mode}")

    sort_by = "elo" if mode == "duels" else "kd"

    add_to_url = ""

    if duel_class:
        classes = get_duels_classes()
        if duel_class not in classes.keys():
            raise ValueError("Must use a real duel class!")
        add_to_url = f"&class={duel_class}"

    url = f"https://api.hyrivals.gg/leaderboards/{mode}?page={page}&limit={limit}{add_to_url}&sort={sort_by}&order=desc"
    
    return requests.get(url=url).json()

def get_stats(username: str, mode: str) -> dict:

    if mode.lower() not in ("duels, kitpvp"):
        raise ValueError("mode must be duels or kitpvp")

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