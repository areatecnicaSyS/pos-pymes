def obtener_ventas_agrupadas():
  """Obtiene las ventas agrupadas por día y por mes para reportes gerenciales."""
  conn = sqlite3.connect("pos_demo.db")

  # Ventas agrupadas por Día
  query_dia = """
        SELECT DATE(fecha) AS dia, COUNT(id) as total_transacciones, SUM(total) AS total_recaudado
        FROM ventas
        GROUP BY DATE(fecha)
        ORDER BY dia DESC
    """
  df_dia = pd.read_sql_query(query_dia, conn)

  # Ventas agrupadas por Mes (Año-Mes)
  query_mes = """
        SELECT strftime('%Y-%m', fecha) AS mes, COUNT(id) as total_transacciones, SUM(total) AS total_recaudado
        FROM ventas
        GROUP BY strftime('%Y-%m', fecha)
        ORDER BY mes DESC
    """
  df_mes = pd.read_sql_query(query_mes, conn)

  conn.close()
  return df_dia, df_mes