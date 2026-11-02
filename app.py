import io
import pandas as pd
import streamlit as st
from database import (
    actualizar_producto,
    agregar_producto,
    eliminar_producto,
    init_db,
    obtener_categorias,
    obtener_productos,
    obtener_ventas_del_dia,
    registrar_venta,
)

# Configuración de la página con el nuevo nombre y branding
st.set_page_config(
    page_title="POS DEMO - Área Técnica SYS", layout="wide", page_icon="💻"
)

init_db()

if "carrito" not in st.session_state:
  st.session_state.carrito = []

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False
  st.session_state.rol = None

# --- SISTEMA DE LOGIN / CONTRASEÑA ---
if not st.session_state.autenticado:
  st.title("💻 POS DEMO - Área Técnica SYS")
  st.markdown("**Sistema de Punto de Venta y Control**")
  st.markdown("Por favor, ingresa tus credenciales para continuar.")

  with st.form("form_login"):
    usuario_input = st.text_input("Usuario")
    password_input = st.text_input("Contraseña", type="password")
    btn_login = st.form_submit_button("Ingresar")

    if btn_login:
      if usuario_input == "cajero" and password_input == "1234":
        st.session_state.autenticado = True
        st.session_state.rol = "Cajero"
        st.success("¡Bienvenido, Cajero!")
        st.rerun()
      elif usuario_input == "admin" and password_input == "admin2026":
        st.session_state.autenticado = True
        st.session_state.rol = "Administrador"
        st.success("¡Bienvenido, Administrador!")
        st.rerun()
      else:
        st.error("Usuario o contraseña incorrectos.")
  st.stop()

# --- MENÚ LATERAL UNA VEZ AUTENTICADO ---
with st.sidebar:
  # Encabezado con la marca corporativa en el menú
  st.markdown("### 💻 Área Técnica SYS")
  st.caption("Soluciones Tecnológicas")
  st.write(f"👤 **Rol:** {st.session_state.rol}")

  if st.button("🚪 Cerrar Sesión"):
    st.session_state.autenticado = False
    st.session_state.rol = None
    st.rerun()

  st.divider()
  st.title("📌 Menú")

  if st.session_state.rol == "Cajero":
    opcion_menu = st.radio(
        "Selecciona una vista:",
        ["🛒 POS (Caja)", "📊 Ventas y Cierre de Turno"],
    )
  else:
    opcion_menu = st.radio(
        "Selecciona una vista:",
        [
            "🛒 POS (Caja)",
            "📊 Ventas y Cierre de Turno",
            "⚙️ Administración & Excel",
        ],
    )
  st.divider()