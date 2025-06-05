# streamlit_explorar.py

import streamlit as st
from db import get_session
from clases import Usuario, Publicacion, Reaccion

st.set_page_config(page_title="Datos Deportivos", layout="wide")

def mostrar_usuarios():
    st.header("Usuarios")
    session = get_session()
    usuarios = session.query(Usuario).all()

    if not usuarios:
        st.info("No hay usuarios registrados.")
        return

    for u in usuarios:
        with st.expander(f"ID {u.id} → {u.nombre}"):
            st.write(f" Publicaciones:")
            for p in u.publicaciones:
                st.markdown(f"- {p.publicacion}")
            st.write(f" Reacciones:")
            for r in u.reacciones:
                st.markdown(f"- {r.tipo_emocion} en publicación ID {r.publicacion_id}")
    session.close()

def mostrar_publicaciones():
    st.header("Publicaciones")
    session = get_session()
    publicaciones = session.query(Publicacion).all()

    if not publicaciones:
        st.info("No hay publicaciones registradas.")
        return

    for pub in publicaciones:
        with st.expander(f"{pub.publicacion}"):
            st.write(f" Usuario: {pub.usuario.nombre}")
            if pub.reacciones:
                for r in pub.reacciones:
                    st.markdown(f"- {r.usuario.nombre} → {r.tipo_emocion}")
            else:
                st.write(" Sin reacciones")
    session.close()

def mostrar_reacciones():
    st.header("Reacciones")
    session = get_session()
    reacciones = session.query(Reaccion).all()

    if not reacciones:
        st.info("No hay reacciones registradas.")
        return

    for r in reacciones:
        st.markdown(f"- **{r.usuario.nombre}** reaccionó a **\"{r.publicacion.publicacion[:40]}...\"** con emoción: **{r.tipo_emocion}**")
    session.close()

def main():
    st.title(" Explorador de Red Social")

    opcion = st.sidebar.selectbox(
        "Elige qué ver:",
        ("Usuarios", "Publicaciones", "Reacciones")
    )

    if opcion == "Usuarios":
        mostrar_usuarios()
    elif opcion == "Publicaciones":
        mostrar_publicaciones()
    elif opcion == "Reacciones":
        mostrar_reacciones()

if __name__ == "__main__":
    main()
