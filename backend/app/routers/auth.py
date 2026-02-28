from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_admin
from app.database import get_db
from app.models import User
from app.schemas.auth import (
    AdminUserCreate,
    LoginRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_user,
    hash_password,
)


router = APIRouter(prefix="", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(body: UserCreate, db: Session = Depends(get_db)) -> TokenResponse:
    existing = (
        db.query(User)
        .filter((User.username == body.username) | (User.email == body.email))
        .first()
    )
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


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> list[UserResponse]:
    _ = admin
    users = db.query(User).order_by(User.created_at.asc()).all()
    return [UserResponse.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    _ = admin
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    _ = admin
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if body.username is not None and body.username != user.username:
        existing = db.query(User).filter(User.username == body.username).first()
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already in use",
            )
        user.username = body.username

    if body.email is not None and body.email != user.email:
        existing = db.query(User).filter(User.email == body.email).first()
        if existing and existing.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use",
            )
        user.email = body.email

    if body.role is not None:
        user.role = body.role

    if body.is_active is not None:
        user.is_active = body.is_active

    if body.password is not None:
        user.hashed_password = hash_password(body.password)

    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.post("/users", response_model=UserResponse)
def create_user_admin(
    body: AdminUserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
) -> UserResponse:
    _ = admin
    existing = (
        db.query(User)
        .filter((User.username == body.username) | (User.email == body.email))
        .first()
    )
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
        role=body.role,
    )
    user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


@router.get("/trader-choices", response_model=list[UserResponse])
def trader_choices(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[UserResponse]:
    _ = user
    traders = (
        db.query(User)
        .filter(User.role == "trader", User.is_active.is_(True))
        .order_by(User.username.asc())
        .all()
    )
    return [UserResponse.model_validate(u) for u in traders]

