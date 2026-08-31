from fastapi import APIRouter, HTTPException, Depends, status
from app.models.order import OrderCreate, OrderOut
from app.crud import orders as crud
from app.auth.security import get_current_user

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new medicine order.
    Requires authentication. Validates medicine existence and stock availability,
    atomically decrements stock, and calculates total price server-side.
    """
    new_order, error_message, status_code = await crud.create_order(
        user_id=current_user["id"],
        order_data=order
    )
    if error_message:
        raise HTTPException(status_code=status_code, detail=error_message)

    return new_order

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: str):
    """
    Retrieve order details by order ID. Public endpoint.
    """
    order = await crud.get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order
