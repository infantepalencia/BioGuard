from sqlalchemy.orm import Session
from . import models, schemas, auth


#  --- SECCIÓN USUARIOS ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.correo_electronico == email).first()

def create_user(db: Session, usuario: schemas.UsuarioCreate):
    hashed_pw = auth.hash_password(usuario.contrasena)
    
    rol_final = usuario.rol
    if rol_final == 'admin':
        rol_final = 'administrador'

    nuevo_usuario = models.Usuario(
        nombre_completo=usuario.nombre_completo,
        correo_electronico=usuario.correo_electronico,
        contrasena=hashed_pw,
        rol=rol_final
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario



#  --- SECCIÓN ESPECIE ---
def get_especies(db: Session):
    return db.query(models.Especie).filter(models.Especie.nombre_comun != "Fauna No Registrada").all()

# Buscar una sola especie
def get_especie_por_id(db: Session, id_especie: int):
    return db.query(models.Especie).filter(models.Especie.id_especie == id_especie).first()

def create_especie(db: Session, especie: schemas.EspecieCreate):
    nueva = models.Especie(**especie.model_dump())
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva

# Actualizar 
def update_especie(db: Session, id_especie: int, especie_data: schemas.EspecieUpdate):
    especie_db = get_especie_por_id(db, id_especie)
    if not especie_db:
        return None
        
    # Extrae solo los campos que Angular mandó en el cuerpo del JSON para no pisar el resto con NULL
    datos_actualizados = especie_data.model_dump(exclude_unset=True)
    for llave, valor in datos_actualizados.items():
        setattr(especie_db, llave, valor)
        
    db.commit()
    db.refresh(especie_db)
    return especie_db

#  Borrar especie validando integridad de llaves foráneas
def delete_especie(db: Session, id_especie: int) -> bool:
    especie_db = get_especie_por_id(db, id_especie)
    if not especie_db:
        return False
        
    try:
        db.delete(especie_db)
        db.commit()
        return True
    except Exception:
        
        db.rollback()
        return False