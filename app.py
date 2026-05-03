import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración de la página
st.set_page_config(page_title="Control Pro Rancho Flamboyant", layout="wide")

# 2. Función para cargar datos (Optimizado para el nombre de tu archivo)
@st.cache_data
def load_data():
    # El código intentará con ambos nombres por si acaso
    try:
        df = pd.read_csv("RANCHO.csv")
    except:
        df = pd.read_csv("DIMAQUINAS_C.A._RANCHO_FLAMBOYANT.csv")
    
    # Convertir fecha y limpiar montos
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    cols_financieras = ['MONTO BASE USD', 'MONTO PAGADO', 'HONORARIOS', 'COSTO TOTAL']
    for col in cols_financieras:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    return df

try:
    df = load_data()
    
    # Títulos principales
    st.title('🏗️ Sistema de Control Integral: Rancho Flamboyant')
    st.subheader('Gestión de DIMAQUINAS C.A.')

    # 3. Cálculos de métricas (Ingresos, Gastos y Admin Delegada)
    # Filtramos por las clases exactas de tu CSV
    df_ingresos_solo = df[df['CLASE'] == 'INGRESO']
    df_gastos_solo = df[df['CLASE'] == 'GASTO']
    
    total_ing = df_ingresos_solo['MONTO BASE USD'].sum()
    total_gas = df_gastos_solo['MONTO BASE USD'].sum()
    total_adm = df['HONORARIOS'].sum() # Esta es tu administración delegada
    balance = total_ing - total_gas - total_adm

    # Mostrar métricas en la parte superior
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Ingresos", f"${total_ing:,.2f}")
    m2.metric("Egresos (Gastos)", f"${total_gas:,.2f}")
    m3.metric("Admin. Delegada (Honorarios)", f"${total_adm:,.2f}")
    m4.metric("Saldo Disponible", f"${balance:,.2f}")

    st.divider()

    # 4. Organización por Pestañas
    tab_graficas, tab_ingresos, tab_buscador = st.tabs(["📊 Análisis de Egresos", "💰 Listado de Ingresos", "🔍 Buscador de Datos"])

    with tab_graficas:
        # Selector de tiempo para la evolución
        frecuencia = st.radio("Ver evolución temporal:", ["Semanal", "Mensual"], horizontal=True)
        freq_code = 'W' if frecuencia == "Semanal" else 'ME'
        
        st.write(f"### Evolución del Flujo de Caja ({frecuencia})")
        df_flujo = df[df['CLASE'].isin(['INGRESO', 'GASTO'])].copy()
        df_time = df_flujo.groupby([pd.Grouper(key='FECHA', freq=freq_code), 'CLASE'])['MONTO BASE USD'].sum().unstack().fillna(0)
        st.area_chart(df_time)

        st.divider()
        
        # Las 3 gráficas solicitadas: Tipo, Área y Proveedor
        col_1, col_2 = st.columns(2)
        
        with col_1:
            st.write("#### Egresos por Tipo de Partida")
            df_tipo = df_gastos_solo.groupby('TIPO')['MONTO BASE USD'].sum().sort_values()
            fig1, ax1 = plt.subplots()
            df_tipo.plot(kind='barh', color='#ff9999', ax=ax1)
            ax1.set_xlabel("Monto USD")
            st.pyplot(fig1)

            st.write("#### Egresos por Área de la Obra")
            df_area = df_gastos_solo.groupby('AREA')['MONTO BASE USD'].sum().sort_values()
            fig2, ax2 = plt.subplots()
            df_area.plot(kind='barh', color='#ffcc99', ax=ax2)
            ax2.set_xlabel("Monto USD")
            st.pyplot(fig2)

        with col_2:
            st.write("#### Top Proveedores por Monto")
            df_prov = df_gastos_solo.groupby('PROVEEDOR')['MONTO BASE USD'].sum().sort_values(ascending=False).head(15)
            fig3, ax3 = plt.subplots(figsize=(10, 11))
            sns.barplot(x=df_prov.values, y=df_prov.index, palette='Greys_d', ax=ax3)
            ax3.set_xlabel("Monto USD")
            st.pyplot(fig3)

    with tab_ingresos:
        st.write("### Detalle Completo de Ingresos Recibidos")
        # Mostramos la lista de abonos (como los de Luis Azmouz)
        listado_ing = df_ingresos_solo[['FECHA', 'PROVEEDOR', 'DESCRIPCION', 'MONTO BASE USD']].sort_values('FECHA', ascending=False)
        st.dataframe(listado_ing, use_container_width=True)

    with tab_buscador:
        st.write("### Buscador Global en la Base de Datos")
        texto_buscar = st.text_input("Escribe una palabra para buscar (ej: Andamios, Cemento, Azmouz):")
        if texto_buscar:
            # Filtro inteligente que busca en todas las columnas
            df_busqueda = df[df.apply(lambda row: texto_buscar.lower() in row.astype(str).str.lower().values, axis=1)]
            st.write(f"Se encontraron {len(df_busqueda)} registros.")
            st.dataframe(df_busqueda, use_container_width=True)

except Exception as e:
    st.error(f"Error técnico al cargar el sistema: {e}")
    st.info("Revisa que el archivo 'RANCHO.csv' esté subido correctamente a GitHub.")
