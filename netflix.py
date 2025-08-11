import streamlit as st
import pandas as pd
import plotly.express as px
from itertools import chain

# Configuração da página
st.set_page_config(
    page_title="Dashboard de conteúdo da Netflix",
    page_icon="📺",
    layout="wide",
)

# Carrega o CSV corrigindo o link raw
df_selecionado = pd.read_csv(
    "https://raw.githubusercontent.com/gabirdias98-cloud/netflixcontent/main/df_selecionado.csv"
)

# Cria uma nova coluna com a primeira palavra da categoria
import re

# Cria uma nova coluna com a primeira palavra da categoria, ignorando pontuação
df_selecionado['categoria_base'] = df_selecionado['categoria'].str.extract(r'^([A-Za-zÀ-ÿ]+)', expand=False)

# --- Barra lateral: Filtros ---
st.sidebar.header("🔍 Filtros")

# Filtro de Tipo
tipos_disponiveis = sorted(df_selecionado['tipo'].unique())
tipos_selecionados = st.sidebar.multiselect(
    "Tipo", tipos_disponiveis, default=tipos_disponiveis
)

# Filtro de Continente
continentes_disponiveis = sorted(df_selecionado['continente'].unique())
continentes_selecionados = st.sidebar.multiselect(
    "Continente", continentes_disponiveis, default=continentes_disponiveis
)

# Filtro de Categoria (agora usando categoria_base)
categorias_disponiveis = sorted(df_selecionado['categoria_base'].unique())
categorias_selecionadas = st.sidebar.multiselect(
    "Categoria", categorias_disponiveis, default=categorias_disponiveis
)

# --- Filtros especiais para Brazil ---
st.sidebar.markdown("### Filtros especiais para 'Brazil'")
filtro_brasil = st.sidebar.selectbox(
    "Filtrar títulos com 'Brazil':",
    [
        "Todos",
        "Somente quando 'Brazil' é o único país",
        "Quando 'Brazil' aparece junto de outros países"
    ]
)

# --- Filtragem do DataFrame ---
df_filtrado = df_selecionado[
    (df_selecionado['tipo'].isin(tipos_selecionados)) &
    (df_selecionado['continente'].isin(continentes_selecionados)) &
    (df_selecionado['categoria_base'].isin(categorias_selecionadas))
]

# Aplica o filtro especial do Brazil
if filtro_brasil == "Somente quando 'Brazil' é o único país":
    df_filtrado = df_filtrado[df_filtrado['pais'] == "Brazil"]
elif filtro_brasil == "Quando 'Brazil' aparece junto de outros países":
    df_filtrado = df_filtrado[
        df_filtrado['pais'].str.contains("Brazil") & (df_filtrado['pais'] != "Brazil")
    ]

# --- Gráficos ---
# Gráfico de barras de títulos por país
fig = px.bar(
    df_filtrado['pais'].value_counts().reset_index(name='QuantidadePais'),
    x='QuantidadePais',
    y='pais',
    labels={'QuantidadePais': 'País', 'pais': 'Quantidade de Títulos'},
    title='Títulos por País'
)

# Gráfico de barras de títulos por continente
fig_continente = px.bar(
    df_filtrado['continente'].value_counts().reset_index(name='QuantidadeContinente'),
    x='QuantidadeContinente',
    y='continente',
    labels={'index': 'QuantidadeContinente', 'continente': 'Quantidade de Títulos'},
    title='Títulos por Continente'
)

# Gráfico de barras de categorias por continente (usando categoria_base)
fig_cat_cont = px.bar(
    df_filtrado.groupby(['continente', 'categoria_base']).size().reset_index(name='QuantidadeBase'),
    x='continente',
    y='QuantidadeBase',
    color='categoria_base',
    labels={'continente': 'Continente', 'QuantidadeBase': 'Quantidade de Títulos', 'categoria_base': 'Categoria'},
    title='Distribuição de categorias por continente'
)

# Gráfico especial para o filtro do Brazil
fig_brasil = None
fig_outros = None
if filtro_brasil == "Somente quando 'Brazil' é o único país" and not df_filtrado.empty:
    df_brasil_cat = df_filtrado['categoria_base'].value_counts().reset_index()
    df_brasil_cat.columns = ['Categoria', 'Quantidade']
    fig_brasil = px.bar(
        df_brasil_cat,
        x='Categoria',
        y='Quantidade',
        labels={'Categoria': 'Categoria', 'Quantidade': 'Quantidade'},
        title="Quantidade de títulos por categoria (apenas Brasil)"
    )
elif filtro_brasil == "Quando 'Brazil' aparece junto de outros países" and not df_filtrado.empty:
    outros_paises = (
        df_filtrado['pais']
        .str.split(', ')
        .apply(lambda lista: [p for p in lista if p != "Brazil"])
    )
    flat_paises = list(chain.from_iterable(outros_paises))
    paises_df = pd.Series(flat_paises).value_counts().reset_index()
    paises_df.columns = ['País', 'Quantidade']
    fig_outros = px.bar(
        paises_df,
        x='País',
        y='Quantidade',
        title="Quantidade de títulos por país (junto com o Brasil)"
    )

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de nacionalidade dos conteúdos da Netflix")
st.markdown("Explore os dados de nacionalidade do catálogo da Netflix em 2021. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Gerais ---
st.subheader("Métricas gerais")
st.metric("Quantidade de títulos", len(df_filtrado))
st.metric("Qtd. de países únicos", df_filtrado['pais'].nunique())

# --- Gráficos em sequência --- 

st.subheader("Distribuição por país")
st.plotly_chart(fig, use_container_width=True)

if fig_brasil is not None:
        st.subheader("Categorias dos títulos exclusivamente brasileiros")
        st.plotly_chart(fig_brasil, use_container_width=True)

st.subheader("Distribuição por continente")
st.plotly_chart(fig_continente, use_container_width=True)

st.subheader("Distribuição de categorias por continente")
st.plotly_chart(fig_cat_cont, use_container_width=True)

if fig_outros is not None:
        st.subheader("Países que aparecem junto com o Brasil")
        st.plotly_chart(fig_outros, use_container_width=True)
# --- Fim do Dashboard ---







