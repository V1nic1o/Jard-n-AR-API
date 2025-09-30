# app/routers/designs.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas import design as design_schema
from app.crud import design as design_crud
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import user as user_model

router = APIRouter(
    prefix="/designs",
    tags=["designs"],
)

@router.post("/", response_model=design_schema.Design)
def create_design(
    design: design_schema.DesignCreate, 
    db: Session = Depends(get_db), 
    current_user: user_model.User = Depends(get_current_user)
):
    # Llamamos a la función del CRUD para crear el diseño,
    # pasándole el ID del usuario que hemos obtenido del token.
    return design_crud.create_user_design(db=db, design=design, user_id=current_user.id)