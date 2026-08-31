import re
from bson import ObjectId
from bson.errors import InvalidId
from app import database

def medicine_helper(medicine: dict) -> dict:
    """Helper to convert MongoDB document to response-ready dictionary."""
    return {
        "id": str(medicine["_id"]),
        "name": medicine["name"],
        "price": medicine["price"],
        "category": medicine["category"],
        "stock": medicine["stock"],
        "manufacturer": medicine["manufacturer"],
    }

async def create_medicine(data: dict) -> dict:
    """Insert a new medicine document into MongoDB."""
    result = await database.db.medicines.insert_one(data)
    new_medicine = await database.db.medicines.find_one({"_id": result.inserted_id})
    return medicine_helper(new_medicine)

async def get_all_medicines() -> list:
    """Retrieve all medicines from MongoDB."""
    medicines = []
    async for medicine in database.db.medicines.find():
        medicines.append(medicine_helper(medicine))
    return medicines

async def get_medicine_by_id(medicine_id: str) -> dict | None:
    """Retrieve a single medicine by its ObjectId string."""
    try:
        obj_id = ObjectId(medicine_id)
    except InvalidId:
        return None
    medicine = await database.db.medicines.find_one({"_id": obj_id})
    if medicine:
        return medicine_helper(medicine)
    return None

async def search_medicines_by_name(query_name: str) -> list:
    """
    Search medicines by partial name (case-insensitive).
    Uses regex escaping to handle special characters safely.
    """
    escaped_query = re.escape(query_name)
    medicines = []
    cursor = database.db.medicines.find(
        {"name": {"$regex": escaped_query, "$options": "i"}}
    )
    async for medicine in cursor:
        medicines.append(medicine_helper(medicine))
    return medicines

async def update_medicine(medicine_id: str, data: dict) -> dict | None:
    """Update medicine fields by ObjectId string."""
    try:
        obj_id = ObjectId(medicine_id)
    except InvalidId:
        return None
    await database.db.medicines.update_one({"_id": obj_id}, {"$set": data})
    updated = await database.db.medicines.find_one({"_id": obj_id})
    if updated:
        return medicine_helper(updated)
    return None

async def delete_medicine(medicine_id: str) -> bool:
    """Delete a medicine by ObjectId string."""
    try:
        obj_id = ObjectId(medicine_id)
    except InvalidId:
        return False
    result = await database.db.medicines.delete_one({"_id": obj_id})
    return result.deleted_count == 1