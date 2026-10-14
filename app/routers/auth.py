from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..auth import create_access_token
from ..crud import authenticate, create_employee
from ..database import get_db
from ..schemas import EmployeeResponse, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=EmployeeResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    return create_employee(db, payload)


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(access_token=create_access_token(str(user.id)))
