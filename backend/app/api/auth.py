from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import User, Institution
from ..schemas.schemas import UserLogin, UserRegister, UserProvisionAdmin, UserOut, Token
from ..services.auth import (
    verify_password, hash_password, create_access_token, get_current_user,
    require_roles, log_audit
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is disabled")

    access_token = create_access_token(data={"sub": user.id, "role": user.role, "email": user.email})
    log_audit(db, action="USER_LOGIN", resource_type="User", resource_id=str(user.id), user_id=user.id)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=UserOut)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Public registration endpoint.
    Strictly forces role to 'institution_admin' and blocks privilege escalation attempts.
    """
    if user_data.role and user_data.role != "institution_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privilege escalation prohibited: public registration cannot create review_officer or system_admin accounts."
        )

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role="institution_admin",  # Server-enforced: cannot be overridden by public caller
        institution_id=user_data.institution_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_audit(db, action="USER_REGISTERED", resource_type="User", resource_id=str(new_user.id), user_id=new_user.id)
    return new_user

@router.post("/provision", response_model=UserOut)
def provision_privileged_user(
    user_data: UserProvisionAdmin,
    current_user: User = Depends(require_roles(["system_admin"])),
    db: Session = Depends(get_db)
):
    """
    Authorized provisioning endpoint restricted strictly to System Administrators.
    Used for creating AICTE Review Officers or additional Admin accounts.
    """
    if user_data.role not in ["review_officer", "system_admin", "institution_admin"]:
        raise HTTPException(status_code=400, detail="Invalid role specified for provisioning")

    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        institution_id=user_data.institution_id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    log_audit(
        db,
        action="PRIVILEGED_USER_PROVISIONED",
        resource_type="User",
        resource_id=str(new_user.id),
        user_id=current_user.id,
        details={"assigned_role": user_data.role, "provisioned_by": current_user.email}
    )
    return new_user

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
