# app/schemas/design.py
from pydantic import BaseModel
from typing import List

# Cómo se ve un item individual dentro de un diseño
class DesignItemBase(BaseModel):
    item_name: str
    quantity: int

# Qué datos necesitamos para crear un diseño (esto es lo que Unity enviará)
class DesignCreate(BaseModel):
    name: str
    items: List[DesignItemBase]

# Cómo se verá un diseño completo cuando lo devolvamos desde la API
class Design(DesignCreate):
    id: int
    owner_id: int
    screenshot_url: str | None = None

    class Config:
        from_attributes = True