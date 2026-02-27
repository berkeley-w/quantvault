from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas_auth import UserCreate, UserResponse, LoginRequest, TokenResponse
from services.auth import authenticate_user, create_access_token, create_user
from core.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(body: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(
        (User.username == body.username) | (User.email == body.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )

    user = create_user(
        db=db,
        username=body.username,
        email=body.email,
        password=body.password,
        role="trader",
    )
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.model_validate(current_user)


@router.get("/setup")
def setup_info(db: Session = Depends(get_db)):
    has_users = db.query(User).count() > 0
    return {"has_users": has_users}


@router.post("/setup", response_model=TokenResponse)
def setup_admin(body: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    user_count = db.query(User).count()
    if user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin user already set up",
        )
    user = create_user(
        db=db,
        username=body.username,
        email=body.email,
        password=body.password,
        role="admin",
    )
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))

