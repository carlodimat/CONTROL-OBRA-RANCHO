import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Control Pro Rancho Flamboyant", layout="wide")

@st.cache_data
def load_data():
    # Ajusta este nombre si cambiaste el archivo en GitHub
    try:
        df = pd.read_csv("RANCHO.csv")
    except:
        df = pd.read_csv("DIMAQUINAS_C.A._RANCHO_FLAMBOYANT.csv")
    
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    # Limpieza de columnas financieras
    cols = ['MONTO BASE USD', 'MONTO PAGADO', 'HONORARIOS', 'COSTO TOTAL']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()
    st.title('🏗️ Control Integral: Rancho Flamboyant')

    # --- MÉTRICAS DE CABECERA ---
    ing = df[df['CLASE'] == 'INGRESO']['MONTO BASE USD'].sum()
    gas = df[df['CLASE'] == 'GASTO']['MONTO BASE USD'].sum()
    adm = df['HONORARIOS'].sum() # Administración Delegada
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Ingresos", f"${ing:,.2f}")
    c2.metric("Gastos Directos", f"${gas:,.2f}")
    c3.metric("Admin. Delegada", f"${adm:,.2f}")
    c4.metric("Caja Disponible", f"${ing - gas - adm:,.2f}")

    st.divider()

    # --- PESTAÑAS PARA ORGANIZAR EL CONTENIDO ---
    tab1, tab2, tab3 = st.tabs(["📊 Análisis General", "💰 Detalle de Ingresos", "🔍 Buscador y Datos"])

    with tab1:
        vista = st.radio("Frecuencia de las gráficas:", ["Semanal", "Mensual"], horizontal=True)
        periodo = 'W' if vista == "Semanal" else 'ME'
        
        st.subheader(f"Evolución de Flujo ({vista})")
        df_t = df[df['CLASE'].isin(['INGRESO', 'GASTO'])].copy()
        df_time = df_t.groupby([pd.Grouper(key='FECHA', freq=periodo), 'CLASE'])['MONTO BASE USD'].sum().unstack().fillna(0)
        st.area_chart(df_time)

        col_a, col_b = st.columns(2)
        with col_a:
            st.write("### Egresos por Tipo")
            df_tipo = df[df['CLASE'] == 'GASTO'].groupby('TIPO')['MONTO BASE USD'].sum().sort_values()
            fig_a, ax_a = plt.subplots()
            df_tipo.plot(kind='barh', color='skyblue', ax=ax_a)
            st.pyplot(fig_a)
        with col_b:
            st.write("### Distribución de Administración")
            # Mostrar honorarios acumulados por mes
            df_adm_t = df.groupby(pd.Grouper(key='FECHA', freq='ME'))['HONORARIOS'].sum()
            st.line_chart(df_adm_t)

    with tab2:
        st.subheader("Listado Detallado de Ingresos")
        df_ing = df[df['CLASE'] == 'INGRESO'][['FECHA', 'PROVEEDOR', 'DESCRIPCION', 'MONTO BASE USD']].sort_values('FECHA', ascending=False)
        st.dataframe(df_ing, use_container_width=True)
        
        # Gráfica de quién ha aportado más
        st.write("### Concentración de Abonos por Origen")
        df_ing_pie = df_ing.groupby('PROVEEDOR')['MONTO BASE USD'].sum()
        fig_p, ax_p = plt.subplots()
        df_ing_pie.plot(kind='pie', autopct='%1.1f%%', ax=ax_p, cmap='Pastel1')
        ax_p.set_ylabel("")
        st.pyplot(fig_p)

    with tab3:
        st.subheader("Buscador Global")
        query = st.text_input("Escribe el nombre de un proveedor, material o descripción:")
        if query:
            df_res = df[df.apply(lambda row: query.lower() in row.astype(str).str.lower().values, axis=1)]
            st.write(f"Resultados encontrados: {len(df_res)}")
            st.dataframe(df_res, use_container_width=True)
        else:
            st.write("Usa la barra de arriba para filtrar cualquier dato (ej: 'Andamios', 'Azmouz', 'Efectivo').")

except Exception as e:
    st.error(f"Error al cargar la plataforma: {e}")