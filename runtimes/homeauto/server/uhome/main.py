from fastapi import FastAPI
import uvicorn

from .scheduler import Scheduler
from .modules import ModuleRegistry

app = FastAPI(title="uHOME Server Kernel")

scheduler = Scheduler()
modules = ModuleRegistry()

@app.get("/")
def root():
    return {"service": "uhome-server", "status": "running"}

@app.get("/scheduler")
def list_schedule():
    return scheduler.list()

@app.get("/modules")
def list_modules():
    return modules.list()

def run():
    uvicorn.run(app, host="0.0.0.0", port=8788)
