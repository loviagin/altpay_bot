from mongo import orders_collection

async def create_order(order_id: str, price: float, service: str):
    order = {
        "_id": order_id,
        "price": price,
        "service": service,
        "name": None,
        "method": None,
        "contact": None,
        "status": "ожидает данных"
    }
    await orders_collection.insert_one(order)
    print(f"✅ Новый заказ сохранён: {order}")

async def get_order(order_id: str):
    return await orders_collection.find_one({"_id": order_id})

async def update_order(order_id: str, fields: dict):
    await orders_collection.update_one({"_id": order_id}, {"$set": fields})

async def get_all_orders():
    cursor = orders_collection.find()
    return [order async for order in cursor]