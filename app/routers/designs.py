# app/routers/designs.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import json
import cloudinary
import cloudinary.uploader
from typing import List # Importante para la nueva ruta GET

# Importamos la configuración para que se ejecute al iniciar
from app.core import config
from app.schemas import design as design_schema
from app.crud import design as design_crud
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import user as user_model

from fastapi.responses import StreamingResponse
from app.services import pdf_generator
from io import BytesIO

router = APIRouter(
    prefix="/designs",
    tags=["designs"],
)

@router.post("/", response_model=design_schema.Design)
def create_design(
    design_data: str = Form(...),
    screenshot_file: UploadFile = File(...),
    db: Session = Depends(get_db), 
    current_user: user_model.User = Depends(get_current_user)
):
    try:
        design_create = design_schema.DesignCreate.model_validate_json(design_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="El formato del JSON de design_data es inválido.")

    # 1. Subimos la imagen a Cloudinary
    try:
        upload_result = cloudinary.uploader.upload(screenshot_file.file)
        screenshot_url = upload_result.get("secure_url")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir la imagen a Cloudinary: {e}")

    # 2. Creamos el diseño en la BD (ahora pasamos también la URL de la imagen)
    db_design = design_crud.create_user_design(
        db=db, 
        design=design_create, 
        user_id=current_user.id, 
        screenshot_url=screenshot_url
    )
    
    return db_design


# --- NUEVA RUTA PARA LEER LOS DISEÑOS ---
@router.get("/", response_model=List[design_schema.Design])
def read_user_designs(
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    """
    Obtiene una lista de todos los diseños creados por el usuario actual.
    """
    designs = design_crud.get_user_designs(db=db, user_id=current_user.id)
    return designs

# --- NUEVO ENDPOINT PARA GENERAR EL PDF ---
@router.get("/{design_id}/pdf", tags=["designs"])
def download_design_pdf(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # 1. Buscamos el diseño en la base de datos
    db_design = design_crud.get_design_by_id(db=db, design_id=design_id)

    # 2. Verificaciones de seguridad
    if not db_design:
        raise HTTPException(status_code=404, detail="Diseño no encontrado")
    if db_design.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este diseño")

    # 3. Llamamos a nuestro servicio para generar el PDF
    pdf_bytes = pdf_generator.generate_design_pdf(db_design)

    # 4. Devolvemos el PDF como un archivo para descargar
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=diseño_{design_id}.pdf"}
    )