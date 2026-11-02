import sqlite3
from datetime import datetime

# (Mantén las funciones anteriores y añade o actualiza estas)

def registrar_venta(total, metodo_pago, items_carrito):
    """Registra la venta principal y descuenta el stock de los productos."""
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    
    # 1. Insertar venta
    cursor.execute("""
        INSERT INTO ventas (total, metodo_pago)
        VALUES (?, ?)
    """, (total, metodo_pago))
    venta_id = cursor.lastrowid
    
    # 2. Registrar detalle y actualizar stock
    for item in items_carrito:
        cursor.execute("""
            INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
            VALUES (?, ?, ?, ?, ?)
        """, (venta_id, item['id'], 1, item['precio'], item['precio']))
        
        # Descontar stock
        cursor.execute("""
            UPDATE productos SET stock = stock - 1 WHERE id = ?
        """, (item['id'],))
        
    conn.commit()
    conn.close()

def obtener_ventas_del_dia():
    """Obtiene todas las ventas registradas en la fecha actual."""
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    # Filtramos por el día actual (formato YYYY-MM-DD)
    hoy = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT id, fecha, total, metodo_pago 
        FROM ventas 
        WHERE DATE(fecha) = ?
    """, (hoy,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "fecha": r[1], "total": r[2], "metodo": r[3]} for r in rows]