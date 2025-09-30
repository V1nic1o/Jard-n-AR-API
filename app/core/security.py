# app/core/security.py
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# Importaciones nuevas para buscar al usuario
from app.crud import user as user_crud
from app.core.database import get_db
from app.schemas import user as user_schema

# Usamos bcrypt_sha256 para evitar el límite de 72 bytes y mayor seguridad
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Le decimos a FastAPI que el token se enviará en una cabecera de autorización
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- NUEVA FUNCIÓN DE DEPENDENCIA ---
# Esta función se encargará de todo el proceso de validación del token
def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decodificamos el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Buscamos al usuario en la base de datos
    user = user_crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    
    # Devolvemos el objeto de usuario
    return user