
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard 1K", layout="wide")

def carregar_dados():
    url = "https://raw.githubusercontent.com/nicolascaseiro/1K/refs/heads/main/1K.csv"
    df = pd.read_csv(url, encoding='utf-8')
    return df

df = carregar_dados()

df['Gêneros'] = df['Gêneros'].fillna('Desconhecido').astype(str)
df['Artista'] = df['Artista'].fillna('Desconhecido').astype(str)

generos_lista = df['Gêneros'].apply(lambda x: [g.strip() for g in x.split(',')])
artistas_lista = df['Artista'].apply(lambda x: [a.strip() for a in x.split(',')])

df_temp = df.copy()
df_temp = df_temp.assign(Gêneros_lista=generos_lista)
df_temp = df_temp.explode('Gêneros_lista')

artistas_lista_temp = artistas_lista.loc[df_temp.index]
df_temp = df_temp.assign(Artistas_lista=artistas_lista_temp)
df_temp = df_temp.explode('Artistas_lista')

df_temp['Data do Álbum'] = pd.to_datetime(df_temp['Data do Álbum'], errors='coerce', dayfirst=True)
df_temp['Ano'] = df_temp['Data do Álbum'].dt.year
df_temp['Década'] = (df_temp['Ano'] // 10) * 10

st.sidebar.header("Filtros")

decadas_disponiveis = sorted(df_temp['Década'].dropna().unique())
generos_disponiveis = sorted(df_temp['Gêneros_lista'].dropna().unique())
artistas_disponiveis = sorted(df_temp['Artistas_lista'].dropna().unique())

decada_selecionada = st.sidebar.multiselect('Filtrar por Década:', decadas_disponiveis)
genero_selecionado = st.sidebar.multiselect('Filtrar por Gênero:', generos_disponiveis)
artista_selecionado = st.sidebar.multiselect('Filtrar por Artista:', artistas_disponiveis)

df_filtrado = df_temp.copy()

if decada_selecionada:
    df_filtrado = df_filtrado[df_filtrado['Década'].isin(decada_selecionada)]

if genero_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Gêneros_lista'].isin(genero_selecionado)]

if artista_selecionado:
    df_filtrado = df_filtrado[df_filtrado['Artistas_lista'].isin(artista_selecionado)]

indices_filtrados = df_filtrado.index.unique()
df_tabela = df.loc[indices_filtrados].copy()

df_tabela['Data do Álbum'] = pd.to_datetime(df_tabela['Data do Álbum'], errors='coerce', dayfirst=True)
df_tabela['Ano'] = df_tabela['Data do Álbum'].dt.year
df_tabela['Década'] = (df_tabela['Ano'] // 10) * 10

total_musicas_filtradas = pd.Series(
    df_tabela['Música'].str.strip().str.lower() + ' - ' + df_tabela['Artista'].str.strip().str.lower()
).nunique()

st.title("Dashboard 1K")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de músicas", total_musicas_filtradas)
col2.metric("Média Popularidade", f"{df_filtrado['Popularidade'].mean():.2f}")
col3.metric("Total de Artistas", df_filtrado['Artistas_lista'].nunique())
col4.metric("Total de Gêneros", df_filtrado['Gêneros_lista'].nunique())

st.markdown("---")

df_grafico = df_filtrado.groupby('Gêneros_lista')['Popularidade'].mean().reset_index()

fig = px.bar(df_grafico,
             x='Gêneros_lista',
             y='Popularidade',
             title='Popularidade Média por Gênero Musical',
             labels={'Gêneros_lista': 'Gênero', 'Popularidade': 'Popularidade Média'},
             color='Popularidade',
             color_continuous_scale='Viridis',
             text=df_grafico['Popularidade'].round(2)
            )

fig.update_traces(textposition='outside', marker_line_width=1.5, marker_line_color='black')
fig.update_layout(
    plot_bgcolor='white',
    title_font=dict(size=24, family='Verdana', color='darkblue'),
    xaxis_title_font=dict(size=18, family='Verdana'),
    yaxis_title_font=dict(size=18, family='Verdana'),
    xaxis_tickangle=-45,
    xaxis_tickfont=dict(size=12, family='Verdana'),
    yaxis=dict(range=[0, 100]),
    margin=dict(l=40, r=40, t=80, b=100)
)

st.plotly_chart(fig, width='stretch')

st.markdown("---")

colunas_exibir = ['Música', 'Artista', 'Gêneros', 'Popularidade', 'Década']
st.dataframe(df_tabela[colunas_exibir])
