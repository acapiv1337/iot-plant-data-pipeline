import asyncio
import logging
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes import router
from api.websocket import manager
from config.settings import settings
from ingestion import mqtt_subscriber
from storage.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IoT Plant Pipeline", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")

# Shared MQTT client (used by routes for manual pump control)
mqtt_client = None


@app.on_event("startup")
async def startup():
    init_db()

    # Wire WebSocket broadcast into the MQTT subscriber
    mqtt_subscriber.set_broadcast_callback(manager.broadcast)

    # Run MQTT loop in a background thread
    global mqtt_client
    mqtt_client = mqtt_subscriber.create_client()

    def _run():
        mqtt_client.loop_forever()

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    logger.info("MQTT subscriber started")


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await asyncio.sleep(30)   # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(ws)
