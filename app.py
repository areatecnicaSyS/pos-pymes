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

    # Desglose por método de pago
    st.subheader("Desglose por Método de Pago")
    df_metodos = df_ventas.groupby("metodo")["total"].sum().reset_index()
    st.dataframe(df_metodos, use_container_width=True)

    st.divider()

    # Detalle de transacciones
    st.subheader("Listado de Ventas del Turno")
    st.dataframe(df_ventas, use_container_width=True)

    # --- BOTÓN DE DESCARGA EN EXCEL DE VENTAS ---
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

    # Sección de Cierre de Caja
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