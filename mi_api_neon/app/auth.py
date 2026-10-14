import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv

load_dotenv()


SECRET_KEY = "mi_clave_secreta_universitaria_123" 
ALGORITHM = "HS256"

# --- FUNCIONES DE CONTRASEÑA (Directas con bcrypt) ---
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# --- FUNCIONES DE TOKEN ---
def create_access_token(data: dict):
    to_encode = data.copy()
    # Expira en 24 horas
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)