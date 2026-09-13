import re
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import Token, UserCreate, UserLogin, UserOut

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Rate limiter — keyed by remote IP.
# Login is capped at 10 attempts/minute to prevent brute-force.
limiter = Limiter(key_func=get_remote_address)


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", slug)


@router.post("/register", response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    org_slug = slugify(user_in.org_name or "default-org")
    org = db.query(Organization).filter(Organization.slug == org_slug).first()
    if not org:
        org = Organization(
            name=user_in.org_name or "Default Organization",
            slug=org_slug,
        )
        db.add(org)
        db.commit()
        db.refresh(org)

    # First user in an org automatically becomes admin
    user_count = db.query(User).filter(User.org_id == org.id).count()
    role = "admin" if user_count == 0 else user_in.role

    user = User(
        org_id=org.id,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_data = {"sub": user.id, "org_id": org.id, "role": user.role}
    access_token = create_access_token(token_data)

    return Token(access_token=access_token, token_type="bearer", user=UserOut.from_orm(user))


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT access token.
    Rate-limited to 10 requests per minute per IP to prevent brute-force attacks.
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    token_data = {"sub": user.id, "org_id": user.org_id, "role": user.role}
    access_token = create_access_token(token_data)

    return Token(access_token=access_token, token_type="bearer", user=UserOut.from_orm(user))


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
