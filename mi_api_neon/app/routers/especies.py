from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database

router = APIRouter(prefix="/especies", tags=["Especies"])

# ==========================================
# 🔵 [READ ALL] - Listar todas las especies
# ==========================================
@router.get("/", response_model=List[schemas.EspecieResponse])
def listar(db: Session = Depends(database.get_db)):
    return crud.get_especies(db)

# ==========================================
# 🔵 [READ BY ID] - Obtener una especie específica
# ==========================================
@router.get("/{id_especie}", response_model=schemas.EspecieResponse)
def obtener_por_id(id_especie: int, db: Session = Depends(database.get_db)):
    especie = crud.get_especie_por_id(db, id_especie)
    if not especie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="La especie solicitada no se encuentra registrada."
        )
    return especie

# ==========================================
# 🟢 [CREATE] - Crear una nueva especie
# ==========================================
@router.post("/", response_model=schemas.EspecieResponse, status_code=status.HTTP_201_CREATED)
def crear(especie: schemas.EspecieCreate, db: Session = Depends(database.get_db)):
    return crud.create_especie(db, especie)

# ==========================================
# 🟡 [UPDATE] - Actualizar datos de una especie
# ==========================================
@router.put("/{id_especie}", response_model=schemas.EspecieResponse)
def actualizar(id_especie: int, especie_data: schemas.EspecieUpdate, db: Session = Depends(database.get_db)):
    especie_actualizada = crud.update_especie(db, id_especie, especie_data)
    if not especie_actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se pudo actualizar. La especie no existe."
        )
    return especie_actualizada

# ==========================================
# 🔴 [DELETE] - Eliminar una especie por su ID
# ==========================================
@router.delete("/{id_especie}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(id_especie: int, db: Session = Depends(database.get_db)):
    exito = crud.delete_especie(db, id_especie)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="No se pudo eliminar. La especie no existe."
        )
    return None