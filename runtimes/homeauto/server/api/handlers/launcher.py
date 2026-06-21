from handlers.state import get_now_playing_state


def get_now_playing() -> dict:
    return get_now_playing_state()


def get_status() -> dict:
    return {"surface": "uhome-launcher", "status": "ready"}
