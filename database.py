from datetime import datetime
import sqlite3
import pandas as pd


def init_db():
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT UNIQUE,
            nombre TEXT NOT NULL,
            categoria_id INTEGER,
            precio_costo REAL NOT NULL,
            precio_venta REAL NOT NULL,
            stock INTEGER NOT NULL,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL,
            metodo_pago TEXT NOT NULL
        )
    """)

  cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

  cursor.execute("SELECT COUNT(*) FROM categorias")
  if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO categorias (nombre) VALUES (?)",
        [
            ("Bebidas",),
            ("Abarrotes",),
            ("Tecnología",),
            ("Cuidado Personal",),
        ],
    )

    cursor.executemany(
        """
            INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            ("7701234567890", "Agua Cristal 600ml", 1, 1200, 2000, 45),
            ("7701234567891", "Gaseosa Postobón 1.5L", 1, 3500, 5000, 20),
            ("7701234567892", "Café Sello Rojo 500g", 2, 9000, 13000, 15),
            ("7701234567893", "Arroz Roa 1000g", 2, 4200, 6000, 30),
            ("7701234567894", "Cable USB Tipo C", 3, 8000, 18000, 12),
            ("7701234567895", "Audífonos Manos Libres", 3, 10000, 22000, 8),
            ("7701234567896", "Crema Dental 150ml", 4, 4500, 7500, 18),
        ],
    )

  conn.commit()
  conn.close()


def obtener_productos():
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  cursor.execute("""
        SELECT p.id, p.codigo_barras, p.nombre, p.precio_costo, p.precio_venta, p.stock, c.nombre 
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
    """)
  rows = cursor.fetchall()
  conn.close()
  return [{
      "id": r[0],
      "codigo": r[1],
      "nombre": r[2],
      "costo": r[3],
      "precio": r[4],
      "stock": r[5],
      "cat": r[6],
  } for r in rows]


def obtener_categorias():
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  cursor.execute("SELECT id, nombre FROM categorias")
  rows = cursor.fetchall()
  conn.close()
  return {r[1]: r[0] for r in rows}


def agregar_producto(codigo, nombre, categoria_id, costo, venta, stock):
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
      (codigo, nombre, categoria_id, costo, venta, stock),
  )
  conn.commit()
  conn.close()


def actualizar_producto(prod_id, nombre, costo, venta, stock):
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        UPDATE productos 
        SET nombre = ?, precio_costo = ?, precio_venta = ?, stock = ?
        WHERE id = ?
    """,
      (nombre, costo, venta, stock, prod_id),
  )
  conn.commit()
  conn.close()


def eliminar_producto(prod_id):
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  cursor.execute("DELETE FROM productos WHERE id = ?", (prod_id,))
  conn.commit()
  conn.close()


def agregar_stock(prod_id, cantidad_a_sumar):
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  cursor.execute(
      """
        UPDATE productos 
        SET stock = stock + ?
        WHERE id = ?
    """,
      (cantidad_a_sumar, prod_id),
  )
  conn.commit()
  conn.close()


def registrar_venta(total, metodo_pago, items_carrito):
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()

  cursor.execute(
      """
        INSERT INTO ventas (total, metodo_pago)
        VALUES (?, ?)
    """,
      (total, metodo_pago),
  )
  venta_id = cursor.lastrowid

  for item in items_carrito:
    cursor.execute(
        """
            INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """,
        (venta_id, item["id"], 1, item["precio"], item["precio"]),
    )

    cursor.execute(
        """
            UPDATE productos SET stock = stock - 1 WHERE id = ?
        """,
        (item["id"],),
    )

  conn.commit()
  conn.close()


def obtener_ventas_del_dia():
  conn = sqlite3.connect("pos_demo.db")
  cursor = conn.cursor()
  hoy = datetime.now().strftime("%Y-%m-%d")
  cursor.execute(
      """
        SELECT id, fecha, total, metodo_pago 
        FROM ventas 
        WHERE DATE(fecha) = ?
    """,
      (hoy,),
  )
  rows = cursor.fetchall()
  conn.close()
  return [
      {"id": r[0], "fecha": r[1], "total": r[2], "metodo": r[3]} for r in rows
  ]


def obtener_ventas_agrupadas():
  """Obtiene las ventas agrupadas por día y por mes para reportes gerenciales."""
  conn = sqlite3.connect("pos_demo.db")

  query_dia = """
        SELECT DATE(fecha) AS dia, COUNT(id) as total_transacciones, SUM(total) AS total_recaudado
        FROM ventas
        GROUP BY DATE(fecha)
        ORDER BY dia DESC
    """
  df_dia = pd.read_sql_query(query_dia, conn)

  query_mes = """
        SELECT strftime('%Y-%m', fecha) AS mes, COUNT(id) as total_transacciones, SUM(total) AS total_recaudado
        FROM ventas
        GROUP BY strftime('%Y-%m', fecha)
        ORDER BY mes DESC
    """
  df_mes = pd.read_sql_query(query_mes, conn)

  conn.close()
  return df_dia, df_mes