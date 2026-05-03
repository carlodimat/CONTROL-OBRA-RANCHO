import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de la página web
st.set_page_config(page_title="Dashboard Palm Beach", layout="wide")
st.title('📊 Dashboard: Palm Beach Plus Complementos y Servicios')

# Función para cargar y limpiar datos (el caché ayuda a que cargue más rápido en internet)
@st.cache_data
def load_data():
    df = pd.read_excel("PALM BEACH PLUS COMPLE.xlsx", skiprows=5)
    
    total_idx = df[df['Service Date'] == 'Total'].index
    if len(total_idx) > 0:
        df = df.loc[:total_idx[0]-1]

    df['Service Date'] = df['Service Date'].ffill()
    df = df[~df['Item Category'].astype(str).str.contains('Sub subtotal')]
    df = df[~df['Transaction Type'].astype(str).str.contains('Subtotal')]
    df = df.dropna(subset=['Item Category'])

    df['Service Date'] = pd.to_datetime(df['Service Date'])
    df['Quantity - sum'] = pd.to_numeric(df['Quantity - sum'], errors='coerce')
    df['Debits - sum'] = pd.to_numeric(df['Debits - sum'], errors='coerce')
    df['Item Category'] = df['Item Category'].str.strip()
    return df

df = load_data()

# Mostrar un pequeño resumen numérico en la web
col1, col2 = st.columns(2)
col1.metric("Ingresos Totales", f"${df['Debits - sum'].sum():,.2f}")
col2.metric("Total Artículos Vendidos", f"{df['Quantity - sum'].sum():,.0f}")

# Crear las gráficas
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Gráfica 1
df_time = df.groupby(df['Service Date'].dt.to_period('M'))['Debits - sum'].sum().reset_index()
df_time['Service Date'] = df_time['Service Date'].astype(str)
axes[0, 0].plot(df_time['Service Date'], df_time['Debits - sum'], marker='o', color='b', linewidth=2)
axes[0, 0].set_title('Ingresos Totales por Mes')
axes[0, 0].set_xlabel('Mes')
axes[0, 0].set_ylabel('Ingresos (Debits)')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, linestyle='--', alpha=0.7)

# Gráfica 2
df_cat_rev = df.groupby('Item Category')['Debits - sum'].sum().sort_values(ascending=False).head(10)
sns.barplot(x=df_cat_rev.values, y=df_cat_rev.index, ax=axes[0, 1], palette='viridis')
axes[0, 1].set_title('Top 10 Categorías por Ingresos')

# Gráfica 3
df_cat_qty = df.groupby('Item Category')['Quantity - sum'].sum().sort_values(ascending=False).head(10)
sns.barplot(x=df_cat_qty.values, y=df_cat_qty.index, ax=axes[1, 0], palette='magma')
axes[1, 0].set_title('Top 10 Categorías por Cantidad Vendida')

# Gráfica 4
last_date = df['Service Date'].max()
thirty_days_ago = last_date - pd.Timedelta(days=30)
df_last_30 = df[df['Service Date'] >= thirty_days_ago]
df_daily = df_last_30.groupby('Service Date')['Debits - sum'].sum().reset_index()
axes[1, 1].plot(df_daily['Service Date'], df_daily['Debits - sum'], marker='x', color='g', linewidth=1.5)
axes[1, 1].set_title('Tendencia de Ingresos Diarios (Últimos 30 días)')
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].grid(True, linestyle='--', alpha=0.7)

plt.tight_layout()

# Enviar la gráfica a Streamlit
st.pyplot(fig)