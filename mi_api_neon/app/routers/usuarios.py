# 📂 app/routers/usuarios.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, database, auth, models

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# ==========================================================
# 🟢 [POST] Registro general / Creación desde CRUD Admin
# ==========================================================
@router.post("/", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, usuario.correo_electronico)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado en la base de datos")

    if usuario.rol == 'admin':
        usuario.rol = 'administrador'

    return crud.create_user(db, usuario)

@router.post("/registro", response_model=schemas.UsuarioResponse)
def registro(usuario: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, usuario.correo_electronico)
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    if usuario.rol == 'admin':
        usuario.rol = 'administrador'
        
    return crud.create_user(db, usuario)

@router.post("/login")
def login(usuario: schemas.UsuarioLogin, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, usuario.correo_electronico)
    if not db_user or not auth.verify_password(usuario.contrasena, db_user.contrasena):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    token = auth.create_access_token(data={"sub": db_user.correo_electronico, "rol": db_user.rol})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id_usuario": db_user.id_usuario,
            "nombre_completo": db_user.nombre_completo,
            "correo_electronico": db_user.correo_electronico,
            "rol": db_user.rol
        }
    }

# ==========================================================
# 🔵 [GET] Listar todos los usuarios
# ==========================================================
@router.get("/", response_model=List[schemas.UsuarioResponse])
@router.get("", response_model=List[schemas.UsuarioResponse])
def listar_usuarios(db: Session = Depends(database.get_db)):
    return db.query(models.Usuario).all()

# ==========================================================
# 🟡 [PATCH] Actualizar usuario
# ==========================================================
@router.patch("/{id_usuario}", response_model=schemas.UsuarioResponse)
def actualizar_usuario(id_usuario: int, usuario_data: schemas.UsuarioUpdate, db: Session = Depends(database.get_db)):
    usr = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usr:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    datos = usuario_data.dict(exclude_unset=True)
    if "rol" in datos and datos["rol"] == "admin":
        datos["rol"] = "administrador"

    for key, value in datos.items():
        setattr(usr, key, value)
        
    db.commit()
    db.refresh(usr)
    return usr

# ==========================================================
# 🔴 [DELETE] Eliminar usuario
# ==========================================================
@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(database.get_db)):
    usr = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usr:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(usr)
    db.commit()
    return {"mensaje": "Usuario eliminado exitosamente de la base de datos"}