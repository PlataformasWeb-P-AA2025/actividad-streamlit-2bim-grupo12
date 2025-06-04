from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey

from config import cadena_base_datos

engine = create_engine(cadena_base_datos)
Base = declarative_base()


class Usuario(Base):
    __tablename__ = 'usuario'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), unique=True)

    publicaciones = relationship("Publicacion", back_populates="usuario")
    reacciones = relationship("Reaccion", back_populates="usuario")

    def __repr__(self):
        return f"Usuario: {self.nombre}"


class Publicacion(Base):
    __tablename__ = 'publicacion'
    id = Column(Integer, primary_key=True)
    publicacion = Column(String(250))  # para guardar el texto de la publicación
    usuario_id = Column(Integer, ForeignKey('usuario.id'))

    usuario = relationship("Usuario", back_populates="publicaciones")
    reacciones = relationship("Reaccion", back_populates="publicacion")

    def __repr__(self):
        return f"Publicacion {self.id}: {self.publicacion}"


class Reaccion(Base):
    __tablename__ = 'reaccion'
    # clave primaria compuesta para evitar que un usuario reaccione más de una vez a la misma publicación
    usuario_id = Column(Integer, ForeignKey('usuario.id'), primary_key=True)
    publicacion_id = Column(Integer, ForeignKey('publicacion.id'), primary_key=True)

    tipo_emocion = Column(String(100))

    usuario = relationship("Usuario", back_populates="reacciones")
    publicacion = relationship("Publicacion", back_populates="reacciones")

    def __repr__(self):
        return f"Reacción: {self.tipo_emocion} (Usuario {self.usuario_id} en Publicación {self.publicacion_id})"


Base.metadata.create_all(engine)
