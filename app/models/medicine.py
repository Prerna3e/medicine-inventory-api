from pydantic import BaseModel, Field

class MedicineBase(BaseModel):
    name: str
    price: float = Field(gt=0)
    category: str
    stock: int = Field(ge=0)
    manufacturer: str

class MedicineCreate(MedicineBase):
    pass

class MedicineOut(MedicineBase):
    id: str