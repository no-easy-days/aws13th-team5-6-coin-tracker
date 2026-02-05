from fastapi import FastAPI
from routers.coin_history import router as coin_history_router

app = FastAPI()
app.include_router(coin_history_router)