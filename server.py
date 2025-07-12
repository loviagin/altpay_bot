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
    print("🛬 Данные запроса:", data, flush=True)

    order_id = data.get("id")
    price = data.get("price")
    service = data.get("service")

    if not order_id or not price or not service:
        print("❌ Недостаточно данных", flush=True)
        return {"success": False, "message": "Недостаточно данных"}

    await create_order(order_id, price, service)
    print("✅ create_order вызвана", flush=True)
    return {"success": True}