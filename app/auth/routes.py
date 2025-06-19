from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from app.auth import schemas, models, utils
from app.core.database import engine, Base
from app.auth.jwt_utils import create_access_token, create_refresh_token
from app.auth.models import PasswordResetToken
from app.auth.utils import generate_reset_token, hash_password
from app.main import logger
from app.auth.deps import get_db

Base.metadata.create_all(bind=engine)

router = APIRouter()


@router.post("/signup", response_model=schemas.UserOut)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = utils.hash_password(user.password)
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_pw,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/signin", response_model= schemas.TokenResponse)
def signin(user: schemas.UserLogin, db: Session = Depends(get_db)):
    logger.debug("Signin request received")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not utils.verify_password(user.password, db_user.hashed_password):
        logger.warning(f"Login failed: incorrect password for {user.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(db_user.id), "role": db_user.role})
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    logger.info(f"User signed in: {user.email}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetWithToken(BaseModel):
    token: str
    new_password: str

@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    token = generate_reset_token()
    token_entry = PasswordResetToken(user_id=user.id, token=token)
    db.add(token_entry)
    db.commit()

    # Simulate email
    return {"message": "Reset token generated", "token": token}

@router.post("/reset-password-token")
def reset_with_token(payload: ResetWithToken, db: Session = Depends(get_db)):
    token_entry = db.query(PasswordResetToken).filter(PasswordResetToken.token == payload.token).first()
    if not token_entry or token_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == token_entry.user_id).first()
    user.hashed_password = hash_password(payload.new_password)

    db.delete(token_entry)
    db.commit()
    return {"message": "Password reset successful"}

