from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import csv

from config import cadena_base_datos
from clases import Usuario, Publicacion, Reaccion

# Crear el engine y la sesión
engine = create_engine(cadena_base_datos)
Session = sessionmaker(bind=engine)
session = Session()

# Leer usuarios csv
with open('DATA/usuarios_red_x.csv', 'r', encoding='utf-8') as f:
    data = csv.reader(f)
    next(data)  # Saltar encabezado

    for row in data:
        nombre_usuario = row[0]
        usuario = Usuario(nombre=nombre_usuario)
        session.add(usuario)


# Leer publicaciones csv
with open('DATA/usuarios_publicaciones.csv', 'r', encoding='utf-8') as f:
    data = csv.reader(f, delimiter='|')
    next(data)  # Saltar encabezado

    for row in data:
        nombre_usuario = row[0].strip()
        contenido = row[1].strip()

        # hallar el usuario que le pertenece a esa publicacion
        usuario = session.query(Usuario).filter_by(nombre=nombre_usuario).first()

        if usuario:
            publicacion = Publicacion(publicacion=contenido, usuario=usuario)
            session.add(publicacion)


# Leer reacciones csv
with open('DATA/usuario_publicacion_emocion.csv', 'r', encoding='utf-8') as f:
    data = csv.reader(f,  delimiter='|')
    next(data)  # Saltar encabezado

    for row in data:
        nombre_usuario = row[0].strip()
        comentario = row[1].strip()
        emocion = row[2].strip()

        # hallar el usuario en la base de datos
        usuario = session.query(Usuario).filter_by(nombre=nombre_usuario).first()

        # hallar la publicación por texto
        publicacion = session.query(Publicacion).filter_by(publicacion=comentario).first()

        if usuario and publicacion:
            reaccion = Reaccion(
                usuario_id=usuario.id,
                publicacion_id=publicacion.id,
                tipo_emocion=emocion
            )
            session.add(reaccion)

# confirmar
session.commit()