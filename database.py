import sqlite3

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

    cursor.execute("SELECT COUNT(*) FROM categorias")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO categorias (nombre) VALUES (?)", [
            ('Bebidas',), ('Abarrotes',), ('Tecnología',), ('Cuidado Personal',)
        ])
        
        cursor.executemany("""
            INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ('7701234567890', 'Agua Cristal 600ml', 1, 1200, 2000, 45),
            ('7701234567891', 'Gaseosa Postobón 1.5L', 1, 3500, 5000, 20),
            ('7701234567892', 'Café Sello Rojo 500g', 2, 9000, 13000, 15),
            ('7701234567893', 'Arroz Roa 1000g', 2, 4200, 6000, 30),
            ('7701234567894', 'Cable USB Tipo C', 3, 8000, 18000, 12),
            ('7701234567895', 'Audífonos Manos Libres', 3, 10000, 22000, 8),
            ('7701234567896', 'Crema Dental 150ml', 4, 4500, 7500, 18)
        ])
        
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
    return [{"id": r[0], "codigo": r[1], "nombre": r[2], "costo": r[3], "precio": r[4], "stock": r[5], "cat": r[6]} for r in rows]

def obtener_categorias():
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM categorias")
    rows = cursor.fetchall()
    conn.close()
    return {r[1]: r[0] for r in rows} # Retorna diccionario {"Categoría": id}

def agregar_producto(codigo, nombre, categoria_id, costo, venta, stock):
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (codigo_barras, nombre, categoria_id, precio_costo, precio_venta, stock)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (codigo, nombre, categoria_id, costo, venta, stock))
    conn.commit()
    conn.close()

def actualizar_producto(prod_id, nombre, costo, venta, stock):
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos 
        SET nombre = ?, precio_costo = ?, precio_venta = ?, stock = ?
        WHERE id = ?
    """, (nombre, costo, venta, stock, prod_id))
    conn.commit()
    conn.close()

def eliminar_producto(prod_id):
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (prod_id,))
    conn.commit()
    conn.close()