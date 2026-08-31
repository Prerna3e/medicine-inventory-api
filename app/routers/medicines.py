from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.models.medicine import MedicineCreate, MedicineOut
from app.crud import medicines as crud
from app.auth.security import get_current_user

router = APIRouter(prefix="/medicines", tags=["Medicines"])

@router.post("/", response_model=MedicineOut, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine: MedicineCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new medicine entry. Requires JWT authentication.
    """
    new_medicine = await crud.create_medicine(medicine.model_dump())
    return new_medicine

@router.get("/", response_model=list[MedicineOut])
async def list_medicines():
    """
    List all medicines in the catalog. Public endpoint.
    """
    return await crud.get_all_medicines()

@router.get("/search", response_model=list[MedicineOut])
async def search_medicines(name: str = Query(..., min_length=1, description="Partial or full medicine name")):
    """
    Search medicines by partial name (case-insensitive). Public endpoint.
    Must be defined before /{medicine_id} to avoid path parameter matching.
    """
    return await crud.search_medicines_by_name(name)

@router.get("/{medicine_id}", response_model=MedicineOut)
async def get_medicine(medicine_id: str):
    """
    Retrieve medicine details by ID. Public endpoint.
    """
    medicine = await crud.get_medicine_by_id(medicine_id)
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return medicine

@router.put("/{medicine_id}", response_model=MedicineOut)
async def update_medicine(
    medicine_id: str,
    medicine: MedicineCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing medicine. Requires JWT authentication.
    """
    updated = await crud.update_medicine(medicine_id, medicine.model_dump())
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return updated

@router.delete("/{medicine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medicine(
    medicine_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a medicine by ID. Requires JWT authentication.
    """
    deleted = await crud.delete_medicine(medicine_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
    return None