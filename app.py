import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Control de Obra PRO", layout="wide")

@st.cache_data
def load_data():
    # Usamos el nombre que me confirmaste
    df = pd.read_csv("RANCHO.csv")
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    # Asegurar limpieza de montos
    for col in ['MONTO BASE USD', 'MONTO PAGADO', 'COSTO TOTAL']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()
    
    st.title('🏗️ Sistema de Control: Rancho Flamboyant')
    
    # --- BARRA LATERAL (FILTROS Y BÚSQUEDA) ---
    st.sidebar.header("🔍 Panel de Control")
    
    # 1. Buscador de palabras
    search_query = st.sidebar.text_input("Buscar en Descripción o Proveedor", "")
    
    # 2. Selector de Tiempo
    vista_tiempo = st.sidebar.radio("Ver historial por:", ["Mensual", "Semanal"])
    
    # 3. Filtro de Clase
    clases_disponibles = df['CLASE'].unique()
    clases_seleccionadas = st.sidebar.multiselect("Filtrar por Clase:", clases_disponibles, default=['INGRESO', 'GASTO'])

    # Aplicar filtros al DF
    mask = df['CLASE'].isin(clases_seleccionadas)
    if search_query:
        mask = mask & (df['DESCRIPCION'].str.contains(search_query, case=False, na=False) | 
                       df['PROVEEDOR'].str.contains(search_query, case=False, na=False))
    
    df_filtrado = df[mask]

    # --- MÉTRICAS ---
    ing = df[df['CLASE'] == 'INGRESO']['MONTO BASE USD'].sum()
    gas = df[df['CLASE'] == 'GASTO']['MONTO BASE USD'].sum()
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Ingresos", f"${ing:,.2f}")
    m2.metric("Total Gastos", f"${gas:,.2f}")
    m3.metric("Disponible", f"${ing - gas:,.2f}")

    st.divider()

    # --- GRÁFICA TEMPORAL (SEMANAL O MENSUAL) ---
    st.subheader(f"📈 Evolución de Flujo de Caja ({vista_tiempo})")
    periodo = 'ME' if vista_tiempo == "Mensual" else 'W'
    df_time = df[df['CLASE'].isin(['INGRESO', 'GASTO'])].copy()
    df_time_grouped = df_time.groupby([pd.Grouper(key='FECHA', freq=periodo), 'CLASE'])['MONTO BASE USD'].sum().unstack().fillna(0)
    
    st.area_chart(df_time_grouped)

    # --- ANÁLISIS DE INGRESOS Y GASTOS ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.write("### 📥 Detalle de Ingresos")
        df_ing_det = df[df['CLASE'] == 'INGRESO'].groupby('PROVEEDOR')['MONTO BASE USD'].sum().sort_values(ascending=False)
        if not df_ing_det.empty:
            fig_ing, ax_ing = plt.subplots()
            df_ing_det.plot(kind='pie', autopct='%1.1f%%', ax=ax_ing, cmap='Greens')
            ax_ing.set_ylabel("")
            st.pyplot(fig_ing)
        else:
            st.info("No hay ingresos para mostrar.")

    with c2:
        st.write("### 📤 Gastos por Partida")
        df_gas_det = df_filtrado[df_filtrado['CLASE'] == 'GASTO'].groupby('TIPO')['MONTO BASE USD'].sum().sort_values()
        if not df_gas_det.empty:
            fig_gas, ax_gas = plt.subplots()
            df_gas_det.plot(kind='barh', color='orange', ax=ax_gas)
            st.pyplot(fig_gas)

    # --- BUSCADOR DE DATOS ---
    st.write("### 📋 Listado de Movimientos")
    st.dataframe(df_filtrado[['FECHA', 'CLASE', 'PROVEEDOR', 'DESCRIPCION', 'MONTO BASE USD']], use_container_width=True)

except Exception as e:
    st.error(f"Error de configuración: {e}")