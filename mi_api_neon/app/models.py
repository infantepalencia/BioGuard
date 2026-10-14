from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(255), nullable=False)
    correo_electronico = Column(String(255), unique=True, nullable=False)
    contrasena = Column(Text, nullable=False)
    rol = Column(String, nullable=False) 

    incidentes_reportados = relationship("Incidente", foreign_keys="Incidente.id_usuario_ciudadano", back_populates="ciudadano")
    incidentes_atendidos = relationship("Incidente", foreign_keys="Incidente.id_usuario_oficial", back_populates="oficial")
    tickets = relationship("TicketSoporte", back_populates="emisor")

class Especie(Base):
    __tablename__ = "especies"

    id_especie = Column(Integer, primary_key=True, index=True)
    nombre_comun = Column(String(255), nullable=False)
    nombre_cientifico = Column(String(255))
    estado_conservacion = Column(String)
    descripcion = Column(Text)
    url_imagen = Column(Text)

    incidentes = relationship("Incidente", back_populates="especie")

class Incidente(Base):
    __tablename__ = "incidentes"

    id_incidente = Column(Integer, primary_key=True, index=True)
    id_usuario_ciudadano = Column(Integer, ForeignKey("usuarios.id_usuario"))
    
    # 🔹 id_especie ahora es opcional (nullable=True)
    id_especie = Column(Integer, ForeignKey("especies.id_especie"), nullable=True)
    
    # 🔹 Nuevo campo para guardar el texto libre reportado por el ciudadano
    nombre_reportado = Column(String(255), nullable=True)

    ubicacion = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.datetime.utcnow)
    prioridad = Column(String)
    estado = Column(String, default="Recibido")
    id_usuario_oficial = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=True)
    
    descripcion = Column(Text, nullable=True)
    imagen_base64 = Column(Text, nullable=True)

    ciudadano = relationship("Usuario", foreign_keys=[id_usuario_ciudadano], back_populates="incidentes_reportados")
    oficial = relationship("Usuario", foreign_keys=[id_usuario_oficial], back_populates="incidentes_atendidos")
    especie = relationship("Especie", back_populates="incidentes")

class TicketSoporte(Base):
    __tablename__ = "tickets_soporte"

    id_ticket = Column(Integer, primary_key=True, index=True)
    id_usuario_emisor = Column(Integer, ForeignKey("usuarios.id_usuario"))
    asunto = Column(String(255), nullable=False)
    descripcion = Column(Text, nullable=False)
    estado_ticket = Column(String, default="Abierto")

    emisor = relationship("Usuario", back_populates="tickets")