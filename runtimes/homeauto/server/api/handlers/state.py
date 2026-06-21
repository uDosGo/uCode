from datetime import datetime, timezone


_NOW_PLAYING = {
    "state": "idle",
    "target": "default",
    "media": "",
    "updated_at": datetime.now(timezone.utc).isoformat(),
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def set_now_playing(target: str, media: str) -> dict:
    _NOW_PLAYING["state"] = "playing"
    _NOW_PLAYING["target"] = target
    _NOW_PLAYING["media"] = media
    _NOW_PLAYING["updated_at"] = _now_iso()
    return dict(_NOW_PLAYING)


def clear_now_playing(target: str) -> dict:
    _NOW_PLAYING["state"] = "idle"
    _NOW_PLAYING["target"] = target
    _NOW_PLAYING["media"] = ""
    _NOW_PLAYING["updated_at"] = _now_iso()
    return dict(_NOW_PLAYING)


def get_now_playing_state() -> dict:
    return dict(_NOW_PLAYING)
