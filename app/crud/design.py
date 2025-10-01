# app/crud/design.py
from sqlalchemy.orm import Session
from app.models import design as design_model
from app.schemas import design as design_schema

def create_user_design(db: Session, design: design_schema.DesignCreate, user_id: int, screenshot_url: str):
    # Creamos el objeto principal del diseño, incluyendo la URL de la imagen
    db_design = design_model.Design(
        name=design.name, 
        owner_id=user_id,
        screenshot_url=screenshot_url # <-- Nuevo
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)

    # Añadimos los items (esto no cambia)
    for item in design.items:
        db_item = design_model.DesignItem(
            item_name=item.item_name,
            quantity=item.quantity,
            design_id=db_design.id
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_design)
    return db_design

# --- NUEVA FUNCIÓN PARA OBTENER DISEÑOS ---
def get_user_designs(db: Session, user_id: int):
    return db.query(design_model.Design).filter(design_model.Design.owner_id == user_id).all()

# --- NUEVA FUNCIÓN ---
def get_design_by_id(db: Session, design_id: int):
    return db.query(design_model.Design).filter(design_model.Design.id == design_id).first()