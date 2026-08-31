from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import DuplicateKeyError
from app import database

def user_helper(user: dict) -> dict:
    """Helper to convert MongoDB user document to response format."""
    return {
        "id": str(user["_id"]),
        "username": user["username"],
    }

async def get_user_by_username(username: str) -> dict | None:
    """Find a user document by username."""
    user = await database.db.users.find_one({"username": username})
    return user

async def get_user_by_id(user_id: str) -> dict | None:
    """Find a user document by its ObjectId string."""
    try:
        obj_id = ObjectId(user_id)
    except InvalidId:
        return None
    user = await database.db.users.find_one({"_id": obj_id})
    return user

async def create_user(user_data: dict) -> dict | None:
    """
    Insert a new user document.
    Returns the created user or None if duplicate username.
    """
    try:
        result = await database.db.users.insert_one(user_data)
        new_user = await database.db.users.find_one({"_id": result.inserted_id})
        return user_helper(new_user)
    except DuplicateKeyError:
        return None
