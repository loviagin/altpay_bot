orders = {}

def create_order(order_id, price, service):
    orders[order_id] = {
        "id": order_id,
        "price": price,
        "service": service,
        "name": None,
        "method": None,
        "contact": None,
        "status": "ожидает данных"
    }

def get_order(order_id):
    return orders.get(order_id)