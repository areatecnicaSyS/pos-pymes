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
  try:
    st.image("imagen_circular_recortada (12).png", use_container_width=True)
  except:
    pass

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

# ==========================================
# VISTA 1: POS (CAJA RÁPIDA CON BOTONES)
# ==========================================
if opcion_menu == "🛒 POS (Caja)":
  productos = obtener_productos()
  categorias_map = obtener_categorias()
  lista_categorias = ["Todas"] + list(categorias_map.keys())

  st.title("🛒 POS DEMO - Área Técnica SYS")
  st.caption("Sistema de caja rápida para ventas en mostrador")

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

  with st.sidebar:
    st.header("🧾 Carrito de Ventas")
    if not st.session_state.carrito:
      st.info("El carrito está vacío.")
    else:
      total = sum(item["precio"] for item in st.session_state.carrito)
      for i, item in enumerate(st.session_state.carrito):
        col_item, col_del = st.columns([4, 1])
        col_item.write(f"**{item['nombre']}** - ${item['precio']:,.0f}")
        if col_del.button("❌", key=f"del_{i}"):
          st.session_state.carrito.pop(i)
          st.rerun()

      st.divider()
      st.markdown(f"### **Total: ${total:,.0f}**")
      metodo = st.selectbox(
          "Método de Pago", ["Efectivo", "Transferencia / QR", "Tarjeta"]
      )

      if st.button(
          "🔴 Procesar Venta", type="primary", use_container_width=True
      ):
        registrar_venta(total, metodo, st.session_state.carrito)
        st.success(f"¡Venta de ${total:,.0f} registrada con éxito! ({metodo})")
        st.session_state.carrito = []
        st.rerun()

# ==========================================
# VISTA 2: VENTAS Y CIERRE DE TURNO
# ==========================================
elif opcion_menu == "📊 Ventas y Cierre de Turno":
  st.title("📊 Resumen del Día y Cierre de Turno")

  ventas_hoy = obtener_ventas_del_dia()

  if not ventas_hoy:
    st.info(
        "No se han registrado ventas hoy. ¡Empieza a vender desde la pestaña"
        " POS!"
    )
  else:
    df_ventas = pd.DataFrame(ventas_hoy)

    total_recaudado = df_ventas["total"].sum()
    total_transacciones = len(df_ventas)

    c1, c2 = st.columns(2)
    c1.metric("💰 Total Ingresos Hoy", f"${total_recaudado:,.0f}")
    c2.metric("🧾 Transacciones Realizadas", total_transacciones)

    st.divider()

    st.subheader("Desglose por Método de Pago")
    df_metodos = df_ventas.groupby("metodo")["total"].sum().reset_index()
    st.dataframe(df_metodos, use_container_width=True)

    st.divider()

    st.subheader("Listado de Ventas del Turno")
    st.dataframe(df_ventas, use_container_width=True)

    st.subheader("📥 Exportar Reporte de Turno")
    buffer_ventas = io.BytesIO()
    with pd.ExcelWriter(buffer_ventas, engine="openpyxl") as writer:
      df_ventas.to_excel(writer, index=False, sheet_name="Ventas_Del_Dia")
      df_metodos.to_excel(writer, index=False, sheet_name="Resumen_Metodos")

    st.download_button(
        label="📊 Descargar Reporte de Ventas en Excel (.xlsx)",
        data=buffer_ventas.getvalue(),
        file_name="Cierre_Turno_Ventas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="secondary",
    )

    st.markdown("---")
    st.subheader("🔒 Realizar Cierre de Turno")

    efectivo_teorico = (
        df_ventas[df_ventas["metodo"] == "Efectivo"]["total"].sum()
        if "Efectivo" in df_ventas["metodo"].values
        else 0
    )

    with st.form("form_cierre"):
      st.write(
          "Dinero esperado en efectivo en caja según el sistema:"
          f" **${efectivo_teorico:,.0f}**"
      )
      efectivo_en_caja = st.number_input(
          "Ingrese el dinero contado físicamente en la caja:",
          min_value=0.0,
          step=1000.0,
      )
      observaciones = st.text_area("Observaciones del Turno (Opcional)")

      if st.form_submit_button("✅ Confirmar y Finalizar Turno"):
        diferencia = efectivo_en_caja - efectivo_teorico
        st.success(
            "¡Cierre de turno realizado correctamente! Cuadre de caja"
            f" procesado. Diferencia: ${diferencia:,.0f}"
        )

# ==========================================
# VISTA 3: ADMINISTRACIÓN & EXCEL (SOLO ADMIN)
# ==========================================
else:
  st.title("⚙️ Administración de Inventario")

  productos = obtener_productos()
  df_productos = pd.DataFrame(productos)

  st.subheader("📥 Exportar Datos")
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