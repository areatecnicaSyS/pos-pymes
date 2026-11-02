# ==========================================
# VISTA 4: ADMINISTRACIÓN TOTAL & EXCEL (SOLO ADMIN)
# ==========================================
else:
  st.title("⚙️ Administración Total de Inventario y Reportes")

  from database import obtener_ventas_agrupadas

  productos = obtener_productos()
  df_productos = pd.DataFrame(productos)
  df_ventas_dia, df_ventas_mes = obtener_ventas_agrupadas()

  # Pestañas de administración y reportes avanzados
  tab1, tab2, tab3, tab4 = st.tabs([
      "📦 Gestionar Inventario",
      "🆕 Crear Producto",
      "📅 Reportes por Día y Mes",
      "📥 Exportar Todo (Excel)",
  ])

  with tab1:
    st.dataframe(df_productos, use_container_width=True)

    st.markdown("### Editar o Eliminar Producto")
    if productos:
      prod_sel_nombre = st.selectbox(
          "Selecciona un producto:",
          [p["nombre"] for p in productos],
          key="sel_edit_admin",
      )
      prod_sel = next(p for p in productos if p["nombre"] == prod_sel_nombre)

      with st.form("form_editar_admin"):
        n_nombre = st.text_input("Nombre", value=prod_sel["nombre"])
        n_costo = st.number_input(
            "Precio Costo", value=float(prod_sel["costo"]), step=500.0
        )
        n_venta = st.number_input(
            "Precio Venta", value=float(prod_sel["precio"]), step=500.0
        )
        n_stock = st.number_input(
            "Stock Base (Edición general)",
            value=int(prod_sel["stock"]),
            step=1,
        )

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
    with st.form("form_agregar_admin"):
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

  with tab3:
    st.subheader("📅 Historial Consolidado de Ventas")

    st.markdown("#### 📆 Ventas Agrupadas por Día")
    if not df_ventas_dia.empty:
      st.dataframe(df_ventas_dia, use_container_width=True)
    else:
      st.info("No hay registros de ventas diarios todavía.")

    st.markdown("#### 🗓️ Ventas Agrupadas por Mes")
    if not df_ventas_mes.empty:
      st.dataframe(df_ventas_mes, use_container_width=True)
    else:
      st.info("No hay registros de ventas mensuales todavía.")

  with tab4:
    st.subheader("📥 Descargar Reporte Gerencial en Excel")
    st.markdown(
        "Este archivo incluirá en diferentes pestañas: El inventario actual,"
        " el consolidado de ventas por día y el consolidado por mes."
    )

    buffer_gerencial = io.BytesIO()
    with pd.ExcelWriter(buffer_gerencial, engine="openpyxl") as writer:
      df_productos.to_excel(writer, index=False, sheet_name="Inventario_Actual")
      if not df_ventas_dia.empty:
        df_ventas_dia.to_excel(
            writer, index=False, sheet_name="Ventas_Por_Dia"
        )
      if not df_ventas_mes.empty:
        df_ventas_mes.to_excel(
            writer, index=False, sheet_name="Ventas_Por_Mes"
        )

    st.download_button(
        label="📊 Descargar Archivo Excel Completo (.xlsx)",
        data=buffer_gerencial.getvalue(),
        file_name="Reporte_Gerencial_Area_Tecnica.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary",
    )