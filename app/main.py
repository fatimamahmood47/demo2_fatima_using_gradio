# app/main.py
from fastapi import FastAPI
from app.routers import raw_order
from app.routers import normalized_order 

app = FastAPI()
app.include_router(raw_order.router)
app.include_router(normalized_order.router)

