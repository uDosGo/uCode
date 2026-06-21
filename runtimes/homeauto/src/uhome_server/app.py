"""FastAPI application for the standalone uHOME server."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from uhome_server.config import bootstrap_runtime
from uhome_server.routes.containers import router as containers_router
from uhome_server.routes.client import create_client_routes
from uhome_server.routes.dashboard import create_dashboard_routes
from uhome_server.routes.health import router as health_router
from uhome_server.routes.home_assistant import create_ha_routes
from uhome_server.routes.household import create_household_routes
from uhome_server.routes.launcher import create_launcher_routes
from uhome_server.routes.library import router as library_router
from uhome_server.routes.network import router as network_router
from uhome_server.routes.platform import create_platform_routes
from uhome_server.routes.channels import create_channel_routes
from uhome_server.routes.playback import create_playback_routes
from uhome_server.routes.runtime import create_runtime_routes
from uhome_server.routes.usx import router as usx_router


@asynccontextmanager
async def _lifespan(app: FastAPI):
    app.state.bootstrap = bootstrap_runtime()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="uHOME Server", version="0.1.0", lifespan=_lifespan)
    thin_static = Path(__file__).resolve().parent / "static" / "thin"
    if thin_static.is_dir():
        app.mount("/static/thin", StaticFiles(directory=str(thin_static)), name="thin_static")
    app.include_router(health_router)
    app.include_router(create_dashboard_routes())
    app.include_router(create_ha_routes())
    app.include_router(create_household_routes())
    app.include_router(create_launcher_routes())
    app.include_router(create_platform_routes())
    app.include_router(create_client_routes())
    app.include_router(create_channel_routes())
    app.include_router(create_playback_routes())
    app.include_router(create_runtime_routes())
    app.include_router(library_router)
    app.include_router(containers_router)
    app.include_router(network_router)
    app.include_router(usx_router)
    return app


app = create_app()
