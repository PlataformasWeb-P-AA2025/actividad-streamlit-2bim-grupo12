# streamlit_explorar.py
import pandas as pd                              # Manipulación de datos en forma tabular
import matplotlib.pyplot as plt                  # Gráficos tradicionales como pie chart
import streamlit as st                           # Librería para construir la interfaz web
import plotly.express as px                      # Gráficos interactivos y personalizables
import plotly.graph_objects as go                # Gráficos avanzados (no usado directamente aquí)
from db import get_session                       # Función que nos da la sesión con la base de datos
from clases import Usuario, Publicacion, Reaccion # Clases ORM para acceder a las tablas

# utilizamos Plotly y Matplotlib para representar consultas

# comfiguracion incial de streamlit
st.set_page_config(page_title="Datos Base de Datos Red Social", layout="wide")  # Título del navegador y diseño ancho

def mostrar_usuarios():
    st.header("Usuarios")
    session = get_session()
    usuarios = session.query(Usuario).all()

    if not usuarios:
        st.info("No hay usuarios registrados.")
        return

    for u in usuarios:
        with st.expander(f"ID {u.id} → {u.nombre}"):
            st.write(" Publicaciones:")
            for p in u.publicaciones:
                st.markdown(f"- {p.publicacion}")
            st.write(" Reacciones:")
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
        st.markdown(
            f"- **{r.usuario.nombre}** reaccionó a **\"{r.publicacion.publicacion[:40]}...\"** con emoción: **{r.tipo_emocion}**")
    session.close()

# mostrar publicaciones por usuario
# Permite seleccionar un usuario desde un desplegable.
# Muestra todas sus publicaciones en una columna.
# En paralelo, compara con el resto de usuarios mediante un gráfico interactivo.
# También calcula estadísticas: total, promedio y usuario más activo.
# ==========================================
def publicaciones_por_usuario():
    st.header("Consultar publicaciones por usuario")
    session = get_session()
    usuarios = session.query(Usuario).all()

    if not usuarios:
        st.warning("No hay usuarios registrados.")
        session.close()
        return

    nombres = [u.nombre for u in usuarios]
    col1, col2 = st.columns([1, 2])  # División visual

    with col1:
        seleccionado = st.selectbox("Selecciona un usuario", nombres)
        usuario = session.query(Usuario).filter_by(nombre=seleccionado).first()

        if usuario and usuario.publicaciones:
            st.subheader(f"Publicaciones de {usuario.nombre}")
            for i, p in enumerate(usuario.publicaciones, 1):
                st.markdown(f"**{i}.** {p.publicacion}")
        else:
            st.warning("Este usuario no tiene publicaciones.")

    with col2:
        st.subheader("Cantidad de publicaciones")
        datos_usuarios = [{
            'Usuario': u.nombre,
            'Cantidad': len(u.publicaciones),
            'Seleccionado': u.nombre == seleccionado
        } for u in usuarios]

        df = pd.DataFrame(datos_usuarios)

        if not df.empty:
            fig = px.bar(
                df,
                x='Usuario',
                y='Cantidad',
                title="Publicaciones por Usuario",
                color='Seleccionado',
                color_discrete_map={True: '#1f77b4', False: '#d3d3d3'},
                text='Cantidad'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Estadísticas Generales")
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric("Total Publicaciones", df['Cantidad'].sum())
            with col_b:
                st.metric("Promedio por Usuario", f"{df['Cantidad'].mean():.1f}")
            with col_c:
                st.metric("Usuario Más Activo", df.loc[df['Cantidad'].idxmax(), 'Usuario'])

    session.close()

# dashboard principal
# Muestra el panel principal con métricas globales y visualizaciones.
# Incluye:
# - Totales y promedios (usuarios, publicaciones, reacciones)
# - Gráfico de publicaciones por usuario
# - Visualización de reacciones en distintos formatos
# - Gráfico circular con la distribución de emociones
# ==========================================
def dashboard_general():
    st.header("📊 Dashboard General")
    session = get_session()
    usuarios = session.query(Usuario).all()
    publicaciones = session.query(Publicacion).all()
    reacciones = session.query(Reaccion).all()

    if not usuarios:
        st.warning("No hay datos para mostrar.")
        session.close()
        return

    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total Usuarios", len(usuarios))
    with col2:
        st.metric("📝 Total Publicaciones", len(publicaciones))
    with col3:
        st.metric("❤️ Total Reacciones", len(reacciones))
    with col4:
        promedio_pub = len(publicaciones) / len(usuarios) if usuarios else 0
        st.metric("📊 Promedio Pub/Usuario", f"{promedio_pub:.1f}")

    col_left, col_right = st.columns(2)

    # Publicaciones por usuario
    with col_left:
        datos_pub = [{'Usuario': u.nombre, 'Publicaciones': len(u.publicaciones)} for u in usuarios]
        df_pub = pd.DataFrame(datos_pub)
        if not df_pub.empty:
            fig_pub = px.bar(
                df_pub,
                x='Usuario',
                y='Publicaciones',
                title="📝 Publicaciones por Usuario",
                color='Publicaciones',
                color_continuous_scale='Blues'
            )
            fig_pub.update_layout(height=400)
            st.plotly_chart(fig_pub, use_container_width=True)

    # Reacciones por usuario en distintos formatos
    with col_right:
        tipo_grafico = st.selectbox("Tipo de visualización para reacciones:", ["Top 10 Usuarios", "Gráfico de Dispersión", "Mapa de Calor"])
        datos_reac = [{'Usuario': u.nombre, 'Reacciones': len(u.reacciones), 'Publicaciones': len(u.publicaciones)} for u in usuarios]
        df_reac = pd.DataFrame(datos_reac)

        if not df_reac.empty:
            if tipo_grafico == "Top 10 Usuarios":
                df_top = df_reac.nlargest(10, 'Reacciones')
                fig_reac = px.bar(
                    df_top,
                    x='Reacciones',
                    y='Usuario',
                    title="❤️ Top 10 - Reacciones por Usuario",
                    color='Reacciones',
                    color_continuous_scale='Reds',
                    orientation='h'
                )
            elif tipo_grafico == "Gráfico de Dispersión":
                fig_reac = px.scatter(
                    df_reac,
                    x='Publicaciones',
                    y='Reacciones',
                    title="📊 Publicaciones vs Reacciones",
                    hover_data=['Usuario'],
                    color='Reacciones',
                    size='Reacciones',
                    color_continuous_scale='Reds'
                )
            else:
                df_reac['Cat_Publicaciones'] = pd.cut(df_reac['Publicaciones'], bins=3, labels=['Pocas', 'Moderadas', 'Muchas'])
                df_reac['Cat_Reacciones'] = pd.cut(df_reac['Reacciones'], bins=3, labels=['Pocas', 'Moderadas', 'Muchas'])
                heatmap_data = pd.crosstab(df_reac['Cat_Publicaciones'], df_reac['Cat_Reacciones'])
                fig_reac = px.imshow(
                    heatmap_data,
                    title="🔥 Mapa de Calor: Actividad de Usuarios",
                    labels={'x': 'Reacciones', 'y': 'Publicaciones', 'color': 'Usuarios'},
                    color_continuous_scale='Reds'
                )

            fig_reac.update_layout(height=400)
            st.plotly_chart(fig_reac, use_container_width=True)

    # Gráfico de distribución de tipos de emociones
    if reacciones:
        st.subheader("🎭 Distribución de Tipos de Reacciones")
        tipos_reacciones = {}
        for r in reacciones:
            tipos_reacciones[r.tipo_emocion] = tipos_reacciones.get(r.tipo_emocion, 0) + 1
        df_tipos = pd.DataFrame(list(tipos_reacciones.items()), columns=['Tipo', 'Cantidad'])
        fig_pie = px.pie(df_tipos, values='Cantidad', names='Tipo', title="Distribución de Emociones")
        st.plotly_chart(fig_pie, use_container_width=True)

    session.close()

# main
# Define el menú de navegación.
# Según la opción elegida en el sidebar, ejecuta la función correspondiente.
# ==========================================
def main():
    st.title("🌐 Explorador de Red Social")
    opcion = st.sidebar.selectbox(
        "Elige qué ver:",
        ("Dashboard General", "Usuarios", "Publicaciones", "Reacciones", "Publicaciones por usuario")
    )

    if opcion == "Dashboard General":
        dashboard_general()
    elif opcion == "Usuarios":
        mostrar_usuarios()
    elif opcion == "Publicaciones":
        mostrar_publicaciones()
    elif opcion == "Reacciones":
        mostrar_reacciones()
    elif opcion == "Publicaciones por usuario":
        publicaciones_por_usuario()

# Este bloque garantiza que la app se ejecute
# solo si este archivo es el principal y no está importado como módulo.
if __name__ == "__main__":
    main()
