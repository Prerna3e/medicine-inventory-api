from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client: AsyncIOMotorClient = None
db = None

async def connect_to_mongo():
    global client, db
    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.db_name]
    await create_indexes()

async def create_indexes():
    """
    Creates MongoDB indexes on app startup:
    1. Standard index on `medicines.name`:
       Chosen because regex partial matching (`$regex` with `$options: 'i'`) is used
       for flexible substring matching (e.g. searching 'para' matches 'Paracetamol').
       A standard index supports prefix queries, collation indexing, and general sorting.
       (Note: MongoDB $text index only matches whole stemmed words and cannot match partial substrings).
    2. Standard index on `medicines.category`:
       Optimizes filtering medicines by category.
    3. Unique index on `users.username`:
       Enforces username uniqueness at the database level to prevent race conditions during registration.
    """
    if db is not None:
        await db.medicines.create_index("name")
        await db.medicines.create_index("category")
        await db.users.create_index("username", unique=True)

async def close_mongo_connection():
    global client
    if client is not None:
        client.close()