# app/crud/design.py
from sqlalchemy.orm import Session
from app.models import design as design_model
from app.schemas import design as design_schema

def create_user_design(db: Session, design: design_schema.DesignCreate, user_id: int):
    # Creamos el objeto principal del diseño
    db_design = design_model.Design(
        name=design.name, 
        owner_id=user_id
    )
    db.add(db_design)
    db.commit()
    db.refresh(db_design)

    # Ahora, añadimos cada uno de los items (plantas) asociados a ese diseño
    for item in design.items:
        db_item = design_model.DesignItem(
            item_name=item.item_name,
            quantity=item.quantity,
            design_id=db_design.id
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_design) # Refrescamos para cargar la lista de items
    return db_design