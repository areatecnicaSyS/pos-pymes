import sqlite3

def init_db():
    conn = sqlite3.connect("pos_demo.db")
    cursor = conn.cursor()
    
    # Crear tablas
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

    # Precargar categorías si está vacía
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
        SELECT p.id, p.nombre, p.precio_venta, c.nombre, p.stock 
        FROM productos p
        JOIN categorias c ON p.categoria_id = c.id
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "precio": r[2], "cat": r[3], "stock": r[4]} for r in rows]