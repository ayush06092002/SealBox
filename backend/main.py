from fastapi import FastAPI
from backend.routes import upload, download, auth

from threading import Thread
import time
import os
from datetime import datetime

app = FastAPI()

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(download.router)
