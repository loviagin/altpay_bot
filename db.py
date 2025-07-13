from mongo import orders_collection
from currency_fetcher import fetch_all_rates

# Дефолтные курсы валют (используются если фетчинг не удался)
usd_to_kzt = 523.28
byn_to_kzt = 159.5
rub_to_byn = 3.66

async def create_order(order_id: str, amount: float, service: str):
    # Сначала создаем заказ с базовыми данными
    order = {
        "_id": order_id,
        "amount": amount,
        "service": service,
        "price": None,
        "name": None,
        "method": None,
        "contact": None,
        "status": "ожидает данных"
    }
    await orders_collection.insert_one(order)
    print(f"✅ Новый заказ создан: {order}")
    
    # Фетчим актуальные курсы валют
    print("🔄 Фетчим актуальные курсы валют...")
    rub_to_byn_new, byn_to_kzt_new, usd_to_kzt_new = await fetch_all_rates()
    
    # Используем новые курсы или дефолтные, если фетчинг не удался
    global usd_to_kzt, byn_to_kzt, rub_to_byn
    
    if usd_to_kzt_new is not None:
        usd_to_kzt = usd_to_kzt_new
        print(f"✅ Обновлен курс USD/KZT: {usd_to_kzt}")
    
    if byn_to_kzt_new is not None:
        byn_to_kzt = byn_to_kzt_new
        print(f"✅ Обновлен курс BYN/KZT: {byn_to_kzt}")
    
    if rub_to_byn_new is not None:
        rub_to_byn = rub_to_byn_new
        print(f"✅ Обновлен курс RUB/BYN: {rub_to_byn}")
    
    # Пересчитываем цену с новыми курсами
    calculated_price = summarize(amount)
    if calculated_price is not None:
        final_price = rounded_sum(calculated_price)
        if final_price is not None:
            # Обновляем заказ с рассчитанной ценой
            await update_order(order_id, {"price": final_price})
            print(f"💰 Рассчитана цена заказа: {final_price} RUB")
        else:
            print("⚠️ Не удалось округлить цену заказа")
    else:
        print("⚠️ Не удалось рассчитать цену заказа")

async def get_order(order_id: str):
    return await orders_collection.find_one({"_id": order_id})

async def update_order(order_id: str, fields: dict):
    await orders_collection.update_one({"_id": order_id}, {"$set": fields})

async def get_all_orders():
    cursor = orders_collection.find()
    return [order async for order in cursor]

def summarize(price: float) -> float | None:
    # price in USD
    if price <= 0:
        return None

    kzt_price = price * usd_to_kzt
    byn_price = kzt_price / byn_to_kzt
    byn_plus_commission = byn_price + 3 + (byn_price * 0.01)
    rub_price = byn_plus_commission / rub_to_byn * 100
    total = rub_price + 30 + 100  # 30 is bank commission, 100 is fixed fee
    return total

def rounded_sum(sum_value: float) -> int | None:
    # округляем вверх
    res = int(sum_value)
    if sum_value > res:
        res += 1  # аналог .rounded(.up)

    if res < 130:
        return None

    if res < 1000:
        if res % 100 == 0:
            return res
        else:
            first_num = res // 100
            return (first_num + 1) * 100

    elif res < 10000:
        if res % 100 == 0:
            return res
        else:
            two_nums = res // 100
            return (two_nums + 1) * 100

    elif res < 100000:
        if res % 1000 == 0:
            return res
        else:
            three_nums = res // 1000
            return (three_nums + 1) * 1000

    return None