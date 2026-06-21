from urllib.parse import parse_qs

from handlers.state import clear_now_playing, set_now_playing

def post_start(query_string: str = "") -> dict:
    query = parse_qs(query_string)
    target = query.get("target", ["default"])[0]
    media = query.get("media", [""])[0]
    state = set_now_playing(target=target, media=media)
    return {"status": "started", "target": target, "media": media, "now_playing": state}


def post_stop(query_string: str = "") -> dict:
    query = parse_qs(query_string)
    target = query.get("target", ["default"])[0]
    state = clear_now_playing(target=target)
    return {"status": "stopped", "target": target, "now_playing": state}
