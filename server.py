from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from db import create_order

app = FastAPI()

# Разрешаем доступ с фронтенда (если лендинг на другом домене)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://altpay.lovigin.com"],  # можешь указать конкретный домен
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/save-order")
async def save_order(request: Request):
    data = await request.json()
    order_id = data.get("id")
    price = data.get("price")
    service = data.get("service")

    if not order_id or not price or not service:
        return {"success": False, "message": "Недостаточно данных"}

    create_order(order_id, price, service)
    return {"success": True}