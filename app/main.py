# app/main.py
from fastapi import FastAPI
from app.core.database import engine
# Importamos los nuevos modelos
from app.models import user as user_model, design as design_model
# Importamos los nuevos routers
from app.routers import users, auth, designs

# Esta línea ahora también creará las tablas de diseños
user_model.Base.metadata.create_all(bind=engine)
design_model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jardín AR API",
    # ... (el resto es igual)
)

# Incluimos todos los routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(designs.router) # <-- Añadimos el nuevo router

@app.get("/")
def leer_raiz():
    return {"mensaje": "¡Bienvenido al backend de Jardín AR!"}