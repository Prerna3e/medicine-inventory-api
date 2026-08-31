from fastapi import APIRouter, HTTPException
from app.models.medicine import MedicineCreate, MedicineOut
from app.crud import medicines as crud

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.post("/", response_model=MedicineOut, status_code=201)
async def create_medicine(medicine: MedicineCreate):
    new_medicine = await crud.create_medicine(medicine.model_dump())
    return new_medicine

@router.get("/", response_model=list[MedicineOut])
async def list_medicines():
    return await crud.get_all_medicines()

@router.get("/{medicine_id}", response_model=MedicineOut)
async def get_medicine(medicine_id: str):
    medicine = await crud.get_medicine_by_id(medicine_id)
    if not medicine:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return medicine

@router.put("/{medicine_id}", response_model=MedicineOut)
async def update_medicine(medicine_id: str, medicine: MedicineCreate):
    updated = await crud.update_medicine(medicine_id, medicine.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Medicine not found")
    return updated

@router.delete("/{medicine_id}", status_code=204)
async def delete_medicine(medicine_id: str):
    deleted = await crud.delete_medicine(medicine_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Medicine not found")