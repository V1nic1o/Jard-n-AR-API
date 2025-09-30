# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os

from app.schemas.token import Token # Crearemos este schema nuevo
from app.core import security # Crearemos este módulo nuevo
from app.core.database import get_db # Modificaremos database.py para esto
from app.crud import user as user_crud # Crearemos este módulo nuevo

router = APIRouter(tags=["authentication"])


@router.post("/token", response_model=Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    # 1. Autenticar al usuario (verificar email y contraseña)
    user = user_crud.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Definir cuánto durará el token
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))

    # 3. Crear el token de acceso
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # 4. Devolver el token
    return {"access_token": access_token, "token_type": "bearer"}