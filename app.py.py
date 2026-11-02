import streamlit as st
from database import init_db, obtener_productos

st.set_page_config(page_title="Área Técnica POS", layout="wide", page_icon="🛒")

# Inicializar DB y Estado de la sesión
init_db()

if "carrito" not in st.session_state:
    st.session_state.carrito = []

productos = obtener_productos()
categorias = ["Todas"] + sorted(list(set(p["cat"] for p in productos)))

# --- ENCABEZADO ---
st.title("🛒 POS Comercial para PYMES")
st.caption("Sistema de caja rápida para ventas en mostrador")

# --- BOTONES DE CATEGORÍAS ---
st.subheader("Categorías")
cols_cat = st.columns(len(categorias))
if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Todas"

for i, cat in enumerate(categorias):
    if cols_cat[i].button(cat, use_container_width=True, type="primary" if st.session_state.cat_seleccionada == cat else "secondary"):
        st.session_state.cat_seleccionada = cat
        st.rerun()

st.divider()

# --- CUADRÍCULA DE PRODUCTOS (BOTONES) ---
prods_filtrados = (
    productos if st.session_state.cat_seleccionada == "Todas"
    else [p for p in productos if p["cat"] == st.session_state.cat_seleccionada]
)

st.subheader(f"Catálogo: {st.session_state.cat_seleccionada}")
cols_prod = st.columns(3)

for index, prod in enumerate(prods_filtrados):
    col = cols_prod[index % 3]
    with col:
        texto_boton = f"📦 {prod['nombre']}\n\n💵 ${prod['precio']:,.0f} | Stock: {prod['stock']}"
        if st.button(texto_boton, key=f"btn_{prod['id']}", use_container_width=True):
            st.session_state.carrito.append(prod)
            st.toast(f"Añadido: {prod['nombre']}", icon="✅")
            st.rerun()

# --- PANEL LATERAL: CARRITO DE COMPRAS ---
with st.sidebar:
    st.header("🧾 Carrito de Ventas")
    
    if not st.session_state.carrito:
        st.info("El carrito está vacío. Haz clic en un producto para agregarlo.")
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
        
        metodo = st.selectbox("Método de Pago", ["Efectivo", "Transferencia / QR", "Tarjeta"])
        
        if st.button("🔴 Procesar Venta", type="primary", use_container_width=True):
            st.success(f"¡Venta de ${total:,.0f} realizada con éxito! ({metodo})")
            st.session_state.carrito = []
            st.rerun()
            
        if st.button("Vaciar Carrito", use_container_width=True):
            st.session_state.carrito = []
            st.rerun()