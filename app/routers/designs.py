# app/routers/designs.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status, Response
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
import re # Para limpiar el nombre del archivo

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

# --- ENDPOINT CORREGIDO PARA GENERAR EL PDF CON EL NOMBRE DEL DISEÑO ---
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

    # --- INICIO DE LA CORRECIÓN ---
    # Limpiamos el nombre del diseño para que sea un nombre de archivo válido.
    # Reemplazamos espacios y cualquier caracter no seguro con un guion bajo.
    clean_filename = re.sub(r'[^\w\._-]', '_', db_design.name)
    
    # 4. Devolvemos el PDF como un archivo para descargar con el nombre correcto
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={clean_filename}.pdf"}
    )
    
    # --- NUEVO ENDPOINT PARA ELIMINAR UN DISEÑO ---
@router.delete("/{design_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_design_endpoint(
    design_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user)
):
    # 1. Buscamos el diseño en la base de datos
    db_design = design_crud.get_design_by_id(db=db, design_id=design_id)

    # 2. Verificamos si existe y si pertenece al usuario actual (seguridad)
    if not db_design:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diseño no encontrado")

    if db_design.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso para eliminar este diseño")

    # 3. (Opcional pero recomendado) Eliminar la imagen de Cloudinary
    if db_design.screenshot_url:
        try:
            # Extraemos el 'public_id' de la URL de Cloudinary para decirle cuál borrar
            public_id_with_extension = db_design.screenshot_url.split('/')[-1]
            public_id = public_id_with_extension.rsplit('.', 1)[0]
            cloudinary.uploader.destroy(public_id)
        except Exception as e:
            # Si falla la eliminación en Cloudinary, solo lo registramos en la consola.
            # No detenemos la eliminación del diseño de nuestra base de datos.
            print(f"Advertencia: No se pudo eliminar la imagen de Cloudinary: {e}")

    # 4. Eliminamos el diseño de nuestra base de datos usando la función del CRUD
    design_crud.delete_design(db=db, db_design=db_design)

    # Devolvemos una respuesta vacía (204), que es el estándar para una eliminación exitosa
    return Response(status_code=status.HTTP_204_NO_CONTENT)