# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine
from app.models import user as user_model, design as design_model
from app.routers import users, auth, designs

# Esta línea crea las tablas en tu base de datos (si no existen)
user_model.Base.metadata.create_all(bind=engine)
design_model.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Jardín AR API",
    description="API para la aplicación de diseño de jardines en Realidad Aumentada.",
    version="0.1.0",
)

# --- INICIO DE LA CONFIGURACIÓN DE CORS ---

# Orígenes que tienen permiso para hacer peticiones. 
# El "*" es un comodín que significa "cualquiera". Ideal para desarrollo.
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"], # Permite todas las cabeceras
)

# --- FIN DE LA CONFIGURACIÓN DE CORS ---


# Incluimos todos los routers
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(designs.router)

@app.get("/")
def leer_raiz():
    return {"mensaje": "¡Bienvenido al backend de Jardín AR!"}