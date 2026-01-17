import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração Visual da Página
st.set_page_config(page_title="Minhas Finanças", layout="wide", page_icon="💰")

# Estilização CSS para deixar mais "clean"
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. Menu Lateral
with st.sidebar:
    st.title("📂 Configurações")
    uploaded_file = st.file_uploader("Suba seu extrato (CSV ou Excel)", type=['csv', 'xlsx'])
    
    st.divider()
    st.info("Dica: Sua planilha deve ter colunas como 'Data', 'Descrição', 'Valor' e 'Categoria'.")

# 3. Corpo Principal
st.title("🏦 Dashboard de Extrato Bancário")

if uploaded_file is not None:
    # Carregar Dados
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Garantir que a coluna Valor seja numérica
        # Aqui você deve ajustar o nome da coluna para o que estiver na sua planilha
        col_valor = st.sidebar.selectbox("Selecione a coluna de Valor", df.select_dtypes(include=['number']).columns)
        col_cat = st.sidebar.selectbox("Selecione a coluna de Categoria", df.select_dtypes(include=['object']).columns)

        # Filtro de Categorias no Menu Lateral
        categorias = df[col_cat].unique().tolist()
        selecionadas = st.sidebar.multiselect("Filtrar por Categorias", categorias, default=categorias)
        
        # Filtrando o dataframe
        df_filtrado = df[df[col_cat].isin(selecionadas)]

        # --- KPIs (Indicadores) ---
        c1, c2, c3 = st.columns(3)
        total_gasto = df_filtrado[col_valor].sum()
        media_gasto = df_filtrado[col_valor].mean()
        qtd_transacoes = len(df_filtrado)

        c1.metric("Gasto Total", f"R$ {total_gasto:,.2f}")
        c2.metric("Média por Transação", f"R$ {media_gasto:,.2f}")
        c3.metric("Nº de Transações", qtd_transacoes)

        st.markdown("---")

        # --- Gráficos ---
        col_esq, col_dir = st.columns(2)

        with col_esq:
            st.subheader("Gastos por Categoria")
            fig_pie = px.pie(df_filtrado, names=col_cat, values=col_valor, 
                             hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_dir:
            st.subheader("Histórico de Gastos")
            # Se tiver uma coluna de data, podemos ordenar
            fig_bar = px.bar(df_filtrado, x=df_filtrado.index, y=col_valor, 
                             color=col_cat, color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- Tabela e Download ---
        st.subheader("📋 Detalhamento dos Dados")
        st.dataframe(df_filtrado, use_container_width=True)

        # Botão de Download
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar extrato filtrado (CSV)",
            data=csv,
            file_name='extrato_filtrado.csv',
            mime='text/csv',
        )

    except Exception as e:
        st.error(f"Erro ao processar: {e}")
else:
    st.warning("Aguardando o upload do seu extrato bancário no menu lateral.")