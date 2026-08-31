from datetime import datetime
from pydantic import BaseModel, Field

class OrderItem(BaseModel):
    medicine_id: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

class OrderCreate(BaseModel):
    medicines: list[OrderItem] = Field(min_length=1, description="Order must contain at least one medicine")

class OrderOut(BaseModel):
    id: str
    user_id: str
    medicines: list[OrderItem]
    total_price: float
    status: str = "pending"
    created_at: datetime
