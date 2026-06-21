"""Module entry point for the standalone Home Assistant gateway."""

from uhome_server.services.home_assistant.service import HomeAssistantService

if __name__ == "__main__":
    import uvicorn

    service = HomeAssistantService()
    uvicorn.run(service.app, host="0.0.0.0", port=8765)
