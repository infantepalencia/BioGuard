# 📂 app/routers/incidentes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from .. import models, schemas, database

router = APIRouter(prefix="/incidentes", tags=["Incidentes"])

class ActualizarEstadoRequest(BaseModel):
    nuevo_estado: str  # "Aprobado", "Resuelto", "Rechazado"
    prioridad: Optional[str] = None

# ==========================================================
# 🟢 [CREATE] - Reporte ciudadano
# ==========================================================
@router.post("/", response_model=schemas.IncidenteResponse)
@router.post("", response_model=schemas.IncidenteResponse)
def crear_incidente(incidente: schemas.IncidenteCreate, db: Session = Depends(database.get_db)):
    nombre_buscado = incidente.nombre_especie.strip().title()
    
    especie_existente = db.query(models.Especie).filter(models.Especie.nombre_comun == nombre_buscado).first()
    
    if especie_existente:
        id_especie_final = especie_existente.id_especie
        nombre_guardado = None
    else:
        id_especie_final = None
        nombre_guardado = nombre_buscado

    # Validar que el usuario ciudadano existe si se especificó
    ciudadano_id = incidente.id_usuario_ciudadano
    if ciudadano_id is not None:
        usr_db = db.query(models.Usuario).filter(models.Usuario.id_usuario == ciudadano_id).first()
        if not usr_db:
            ciudadano_id = None

    nuevo_incidente = models.Incidente(
        id_usuario_ciudadano=ciudadano_id,
        id_especie=id_especie_final,  
        nombre_reportado=nombre_guardado,
        ubicacion=incidente.ubicacion,
        prioridad=incidente.prioridad or "Media",
        descripcion=incidente.descripcion,      
        imagen_base64=incidente.imagen_base64,
        estado="Recibido"
    )
    
    db.add(nuevo_incidente)
    db.commit()
    db.refresh(nuevo_incidente)
    
    nuevo_incidente.nombre_especie = especie_existente.nombre_comun if especie_existente else nombre_guardado
    return nuevo_incidente

# ==========================================================
# 🔵 [READ ALL] - Listar incidentes
# ==========================================================
@router.get("/", response_model=List[schemas.IncidenteResponse])
@router.get("", response_model=List[schemas.IncidenteResponse])
def listar_incidentes(db: Session = Depends(database.get_db)):
    incidentes = db.query(models.Incidente).all()
    
    for inc in incidentes:
        if inc.especie:
            inc.nombre_especie = inc.especie.nombre_comun
        else:
            inc.nombre_especie = inc.nombre_reportado or "Especie Desconocida"
            
    return incidentes

# ==========================================================
# 🟡 [PATCH] - Moderar Reporte (Rol Autoridad / Admin)
# ==========================================================
@router.patch("/{id_incidente}/moderar", response_model=schemas.IncidenteResponse)
@router.patch("/{id_incidente}/moderar/", response_model=schemas.IncidenteResponse)
def moderar_incidente(
    id_incidente: int, 
    data: schemas.ModerarIncidente, 
    db: Session = Depends(database.get_db)
):
    incidente = db.query(models.Incidente).filter(models.Incidente.id_incidente == id_incidente).first()
    
    if not incidente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró el incidente con ID {id_incidente}")
        
    if data.nuevo_estado not in ["Aprobado", "Rechazado", "Resuelto"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado inválido.")
    
    # Verificar usuario de oficial si se proporciona un ID válido
    if data.id_usuario_oficial:
        oficial = db.query(models.Usuario).filter(models.Usuario.id_usuario == data.id_usuario_oficial).first()
        if oficial:
            incidente.id_usuario_oficial = data.id_usuario_oficial

    incidente.estado = data.nuevo_estado
    
    db.commit()
    db.refresh(incidente)
    
    if incidente.especie:
        incidente.nombre_especie = incidente.especie.nombre_comun
    else:
        incidente.nombre_especie = incidente.nombre_reportado or "Especie Desconocida"
        
    return incidente

# ==========================================================
# 🟣 [PATCH] - Resolver o Cambiar Estado/Prioridad
# ==========================================================
@router.patch("/{id_incidente}/resolver", response_model=schemas.IncidenteResponse)
@router.patch("/{id_incidente}/resolver/", response_model=schemas.IncidenteResponse)
def resolver_incidente(
    id_incidente: int,
    payload: ActualizarEstadoRequest,
    db: Session = Depends(database.get_db)
):
    incidente = db.query(models.Incidente).filter(models.Incidente.id_incidente == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    incidente.estado = payload.nuevo_estado
    if payload.prioridad:
        incidente.prioridad = payload.prioridad

    db.commit()
    db.refresh(incidente)

    if incidente.especie:
        incidente.nombre_especie = incidente.especie.nombre_comun
    else:
        incidente.nombre_especie = incidente.nombre_reportado or "Especie Desconocida"

    return incidente

# ==========================================================
# 🔴 [DELETE] - Rechazar/Eliminar reporte
# ==========================================================
@router.delete("/{id_incidente}")
@router.delete("/{id_incidente}/")
def eliminar_incidente(id_incidente: int, db: Session = Depends(database.get_db)):
    incidente = db.query(models.Incidente).filter(models.Incidente.id_incidente == id_incidente).first()
    if not incidente:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")
    
    db.delete(incidente)
    db.commit()
    return {"mensaje": "Reporte eliminado exitosamente"}