# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import user as user_schema
from app.crud import user as user_crud
from app.core.database import get_db
from app.core.security import get_current_user # <-- Importamos la nueva función
from app.models import user as user_model # <-- Importamos el modelo para el tipo de dato

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=user_schema.User)
def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado")
    return user_crud.create_user(db=db, user=user)


# --- NUEVA RUTA PROTEGIDA ---
@router.get("/me/", response_model=user_schema.User)
def read_users_me(current_user: user_model.User = Depends(get_current_user)):
    """
    Obtiene el perfil del usuario actual.
    Esta ruta está protegida y requiere autenticación.
    """
    return current_user