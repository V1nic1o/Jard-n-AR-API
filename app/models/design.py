# app/models/design.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Design(Base):
    __tablename__ = "designs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    screenshot_url = Column(String) # Aquí guardaremos la ruta a la foto
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")
    items = relationship("DesignItem", cascade="all, delete-orphan")

class DesignItem(Base):
    __tablename__ = "design_items"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity = Column(Integer)
    design_id = Column(Integer, ForeignKey("designs.id"))