from handlers.health import get_health
from handlers.identity import get_identity
from handlers.launcher import get_now_playing, get_status
from handlers.media import get_browse, get_search
from handlers.playback import post_start, post_stop

GET_ROUTES = {
    "/api/health": get_health,
    "/api/identity": get_identity,
    "/api/media/browse": get_browse,
    "/api/media/search": get_search,
    "/api/now-playing": get_now_playing,
    "/api/launcher/status": get_status,
}

POST_ROUTES = {
    "/api/playback/start": post_start,
    "/api/playback/stop": post_stop,
}


def route_get(path: str, query: str) -> tuple[int, dict]:
    handler = GET_ROUTES.get(path)
    if handler is None:
        return 404, {"error": "not found"}
    if path in ("/api/media/browse", "/api/media/search"):
        return 200, handler(query)
    return 200, handler()


def route_post(path: str, query: str = "") -> tuple[int, dict]:
    handler = POST_ROUTES.get(path)
    if handler is None:
        return 404, {"error": "not found"}
    return 200, handler(query)


def route_request(method: str, path: str, query: str = "") -> tuple[int, dict]:
    if method.upper() == "GET":
        return route_get(path, query)
    if method.upper() == "POST":
        return route_post(path, query)
    return 405, {"error": "method not allowed"}
