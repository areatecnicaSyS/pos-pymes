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
)

st.set_page_config(page_title="Área Técnica POS", layout="wide", page_icon="🛒")

init_db()

if "carrito" not in st.session_state:
  st.session_state.carrito = []

# --- NAVEGACIÓN EN EL SIDEBAR ---
with st.sidebar:
  st.title("📌 Menú")
  opcion_menu = st.radio(
      "Selecciona una vista:", ["🛒 POS (Caja)", "⚙️ Administración & Excel"]
  )
  st.divider()

# ==========================================
# VISTA 1: POS (CAJA RÁPIDA CON BOTONES)
# ==========================================
if opcion_menu == "🛒 POS (Caja)":
  productos = obtener_productos()
  categorias_map = obtener_categorias()
  lista_categorias = ["Todas"] + list(categorias_map.keys())

  st.title("🛒 POS Comercial para PYMES")
  st.caption("Sistema de caja rápida para ventas en mostrador")

  # Categorías como botones
  st.subheader("Categorías")
  cols_cat = st.columns(len(lista_categorias))
  if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Todas"

  for i, cat in enumerate(lista_categorias):
    if cols_cat[i].button(
        cat,
        use_container_width=True,
        type=(
            "primary"
            if st.session_state.cat_seleccionada == cat
            else "secondary"
        ),
    ):
      st.session_state.cat_seleccionada = cat
      st.rerun()

  st.divider()

  # Botones de productos
  prods_filtrados = (
      productos
      if st.session_state.cat_seleccionada == "Todas"
      else [
          p for p in productos if p["cat"] == st.session_state.cat_seleccionada
      ]
  )

  st.subheader(f"Catálogo: {st.session_state.cat_seleccionada}")
  cols_prod = st.columns(3)

  for index, prod in enumerate(prods_filtrados):
    col = cols_prod[index % 3]
    with col:
      texto_boton = (
          f"📦 {prod['nombre']}\n\n💵 ${prod['precio']:,.0f} | Stock:"
          f" {prod['stock']}"
      )
      if st.button(
          texto_boton, key=f"btn_{prod['id']}", use_container_width=True
      ):
        st.session_state.carrito.append(prod)
        st.toast(f"Añadido: {prod['nombre']}", icon="✅")
        st.rerun()

  # Sidebar Carrito
  with st.sidebar:
    st.header("🧾 Carrito de Ventas")
    if not st.session_state.carrito:
      st.info("El carrito está vacío.")
    else:
      total = 0
      for i, item in enumerate(st.session_state.carrito):
        col_item, col_del = st.columns([4, 1])
        col_item.write(f"**{item['nombre']}** - ${item['precio']:,.0f}")
        if col_del.button("❌", key=f"del_{i}"):
          st.session_state.carrito.pop(i)
          st.rerun()
        total += item["precio"]

      st.divider()
      st.markdown(f"### **Total: ${total:,.0f}**")
      metodo = st.selectbox(
          "Método de Pago", ["Efectivo", "Transferencia / QR", "Tarjeta"]
      )

      if st.button(
          "🔴 Procesar Venta", type="primary", use_container_width=True
      ):
        st.success(f"¡Venta de ${total:,.0f} realizada con éxito! ({metodo})")
        st.session_state.carrito = []
        st.rerun()

# ==========================================
# VISTA 2: ADMINISTRACIÓN & DESCARGA EXCEL
# ==========================================
else:
  st.title("⚙️ Administración de Inventario")

  productos = obtener_productos()
  df_productos = pd.DataFrame(productos)

  # --- SECCIÓN: DESCARGA EN EXCEL ---
  st.subheader("📥 Exportar Datos")

  # Generar archivo Excel en memoria
  buffer = io.BytesIO()
  with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    df_productos.to_excel(writer, index=False, sheet_name="Inventario")

  st.download_button(
      label="📊 Descargar Inventario en Excel (.xlsx)",
      data=buffer.getvalue(),
      file_name="Inventario_POS.xlsx",
      mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      type="primary",
  )

  st.divider()

  # --- SECCIÓN: TABLA Y EDICIÓN ---
  tab1, tab2 = st.tabs(
      ["📦 Gestionar Productos Existentes", "➕ Agregar Nuevo Producto"]
  )

  with tab1:
    st.dataframe(df_productos, use_container_width=True)

    st.markdown("### Editar o Eliminar Producto")
    if productos:
      prod_sel_nombre = st.selectbox(
          "Selecciona un producto:", [p["nombre"] for p in productos]
      )
      prod_sel = next(p for p in productos if p["nombre"] == prod_sel_nombre)

      with st.form("form_editar"):
        n_nombre = st.text_input("Nombre", value=prod_sel["nombre"])
        n_costo = st.number_input(
            "Precio Costo", value=float(prod_sel["costo"]), step=500.0
        )
        n_venta = st.number_input(
            "Precio Venta", value=float(prod_sel["precio"]), step=500.0
        )
        n_stock = st.number_input("Stock", value=int(prod_sel["stock"]), step=1)

        c1, c2 = st.columns(2)
        btn_actualizar = c1.form_submit_button("💾 Guardar Cambios")
        btn_eliminar = c2.form_submit_button("🗑️ Eliminar Producto")

        if btn_actualizar:
          actualizar_producto(
              prod_sel["id"], n_nombre, n_costo, n_venta, n_stock
          )
          st.success("¡Producto actualizado exitosamente!")
          st.rerun()

        if btn_eliminar:
          eliminar_producto(prod_sel["id"])
          st.warning("Producto eliminado.")
          st.rerun()

  with tab2:
    categorias_map = obtener_categorias()
    with st.form("form_agregar"):
      a_codigo = st.text_input("Código de Barras (Único)")
      a_nombre = st.text_input("Nombre del Producto")
      a_cat = st.selectbox("Categoría", list(categorias_map.keys()))
      a_costo = st.number_input("Precio Costo", value=0.0, step=500.0)
      a_venta = st.number_input("Precio Venta", value=0.0, step=500.0)
      a_stock = st.number_input("Stock Inicial", value=10, step=1)

      if st.form_submit_button("➕ Crear Producto"):
        if a_codigo and a_nombre:
          cat_id = categorias_map[a_cat]
          agregar_producto(
              a_codigo, a_nombre, cat_id, a_costo, a_venta, a_stock
          )
          st.success(f"Producto '{a_nombre}' guardado con éxito.")
          st.rerun()
        else:
          st.error("Por favor completa el código y el nombre.")