from bson import ObjectId
from bson.errors import InvalidId
from app import db

def medicine_helper(medicine) -> dict:
    return {
        "id": str(medicine["_id"]),
        "name": medicine["name"],
        "price": medicine["price"],
        "category": medicine["category"],
        "stock": medicine["stock"],
        "manufacturer": medicine["manufacturer"],
    }

async def create_medicine(data: dict) -> dict:
    result = await db.medicines.insert_one(data)
    new_medicine = await db.medicines.find_one({"_id": result.inserted_id})
    return medicine_helper(new_medicine)

async def get_all_medicines() -> list:
    medicines = []
    async for medicine in db.medicines.find():
        medicines.append(medicine_helper(medicine))
    return medicines

async def get_medicine_by_id(medicine_id: str):
    try:
        obj_id = ObjectId(medicine_id)
    except InvalidId:
        return None
    medicine = await db.medicines.find_one({"_id": obj_id})
    if medicine:
        return medicine_helper(medicine)
    return None

async def update_medicine(medicine_id: str, data: dict):
    try:
        obj_id = ObjectId(medicine_id)
    except InvalidId:
        return None
    await db.medicines.update_one({"_id": obj_id}, {"$set": data})
    updated = await db.medicines.find_one({"_id": obj_id})
    if updated:
        return medicine_helper(updated)
    return None

async def delete_medicine(medicine_id: str) -> bool:
    try:
        obj_id = ObjectId(medicine_id)
    except InvalidId:
        return False
    result = await db.medicines.delete_one({"_id": obj_id})
    return result.deleted_count == 1