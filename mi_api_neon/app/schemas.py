from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# --- ESQUEMAS DE USUARIO ---
class UsuarioBase(BaseModel):
    nombre_completo: str
    correo_electronico: EmailStr
    rol: str  # 'ciudadano' | 'autoridad' | 'administrador'

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioLogin(BaseModel):
    correo_electronico: EmailStr
    contrasena: str

class UsuarioUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    correo_electronico: Optional[EmailStr] = None
    rol: Optional[str] = None
    contrasena: Optional[str] = None

class UsuarioResponse(UsuarioBase):
    id_usuario: int
    
    class Config:
        from_attributes = True



# --- ESQUEMAS DE ESPECIES ---

class EspecieBase(BaseModel):
    nombre_comun: str
    nombre_cientifico: Optional[str] = None
    estado_conservacion: Optional[str] = "Preocupación Menor" 
    descripcion: Optional[str] = None
    url_imagen: Optional[str] = None

class EspecieCreate(EspecieBase):
    pass

class EspecieUpdate(BaseModel):
    nombre_comun: Optional[str] = None
    nombre_cientifico: Optional[str] = None
    estado_conservacion: Optional[str] = None
    descripcion: Optional[str] = None
    url_imagen: Optional[str] = None

class EspecieResponse(EspecieBase):
    id_especie: int
    
    class Config:
        from_attributes = True



# ESQUEMAS DE INCIDENTES ---
class IncidenteCreate(BaseModel):
    id_usuario_ciudadano: Optional[int] = 1
    nombre_especie: str 
    ubicacion: str
    prioridad: Optional[str] = "Media"
    descripcion: Optional[str] = None 
    imagen_base64: Optional[str] = None 

class ModerarIncidente(BaseModel):
    nuevo_estado: str
    id_usuario_oficial: int

class IncidenteResponse(BaseModel):
    id_incidente: int
    id_usuario_ciudadano: Optional[int] = None
    id_especie: Optional[int] = None
    nombre_reportado: Optional[str] = None
    nombre_especie: Optional[str] = None
    ubicacion: str
    fecha: datetime
    prioridad: str
    estado: str
    id_usuario_oficial: Optional[int] = None
    descripcion: Optional[str] = None
    imagen_base64: Optional[str] = None
    
    class Config:
        from_attributes = True



# --- ESQUEMAS DE TICKETS ---
class TicketCreate(BaseModel):
    id_usuario_emisor: int
    asunto: str
    descripcion: str

class TicketResponse(BaseModel):
    id_ticket: int
    id_usuario_emisor: int
    asunto: str
    descripcion: str
    estado_ticket: str
    
    class Config:
        from_attributes = True