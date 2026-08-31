from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserLogin, UserOut, Token
from app.crud import users as crud
from app.auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    """
    Register a new user.
    Rejects duplicate usernames with 409 Conflict.
    """
    existing_user = await crud.get_user_by_username(user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )

    user_dict = {
        "username": user_in.username,
        "hashed_password": hash_password(user_in.password),
    }

    new_user = await crud.create_user(user_dict)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already registered"
        )
    return new_user

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Authenticate user credentials and return a signed JWT access token.
    """
    user = await crud.get_user_by_username(credentials.username)
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
