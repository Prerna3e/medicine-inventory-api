from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from app import database
from app.models.order import OrderCreate

def order_helper(order: dict) -> dict:
    """Helper to convert MongoDB order document to response format."""
    return {
        "id": str(order["_id"]),
        "user_id": str(order["user_id"]),
        "medicines": order["medicines"],
        "total_price": float(order["total_price"]),
        "status": order.get("status", "pending"),
        "created_at": order["created_at"],
    }

async def create_order(user_id: str, order_data: OrderCreate) -> tuple[dict | None, str | None, int]:
    """
    Process and place an order:
    1. Validates each medicine exists (returns 404 if not found).
    2. Checks stock availability (returns 409 if insufficient).
    3. Calculates total_price server-side from live DB prices.
    4. Atomically decrements stock using filter `{"_id": id, "stock": {"$gte": qty}}`.
    5. Saves the order with status "pending" and UTC created_at.

    Returns:
        (order_dict, None, 201) on success
        (None, error_message, status_code) on failure
    """
    total_price = 0.0
    items_to_decrement = []

    # Step 1 & 2: Validate all medicines and check stock availability
    for item in order_data.medicines:
        try:
            med_obj_id = ObjectId(item.medicine_id)
        except InvalidId:
            return None, f"Medicine ID '{item.medicine_id}' is invalid", 404

        medicine = await database.db.medicines.find_one({"_id": med_obj_id})
        if not medicine:
            return None, f"Medicine with ID '{item.medicine_id}' not found", 404

        if medicine["stock"] < item.quantity:
            return (
                None,
                f"Insufficient stock for '{medicine['name']}'. Requested: {item.quantity}, Available: {medicine['stock']}",
                409,
            )

        item_total = float(medicine["price"]) * item.quantity
        total_price += item_total
        items_to_decrement.append((med_obj_id, item.quantity, medicine["name"]))

    # Step 3: Atomically decrement stock
    for med_id, qty, med_name in items_to_decrement:
        res = await database.db.medicines.update_one(
            {"_id": med_id, "stock": {"$gte": qty}},
            {"$inc": {"stock": -qty}},
        )
        if res.modified_count == 0:
            return (
                None,
                f"Stock conflict while processing '{med_name}'. Please retry.",
                409,
            )

    # Step 4: Insert the order document
    order_doc = {
        "user_id": user_id,
        "medicines": [item.model_dump() for item in order_data.medicines],
        "total_price": round(total_price, 2),
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
    }

    insert_result = await database.db.orders.insert_one(order_doc)
    new_order = await database.db.orders.find_one({"_id": insert_result.inserted_id})
    return order_helper(new_order), None, 201

async def get_order_by_id(order_id: str) -> dict | None:
    """Retrieve an order by its ObjectId string."""
    try:
        obj_id = ObjectId(order_id)
    except InvalidId:
        return None

    order = await database.db.orders.find_one({"_id": obj_id})
    if order:
        return order_helper(order)
    return None
