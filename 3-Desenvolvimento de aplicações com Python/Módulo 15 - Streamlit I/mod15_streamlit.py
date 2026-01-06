import streamlit as st
import pandas as pd
import plotly.express as px

# Cabeçalho
st.title(f"📈 SINASC: RO 2019")
st.subheader("Sistema de Informações sobre Nascidos Vivos", divider=True)
st.markdown("""O Sistema de Informações sobre Nascidos Vivos - SINASC foi implantado oficialmente a partir de 1990, com o objetivo de coletar dados sobre os nascimentos ocorridos em todo o território nacional e fornecer informações sobre natalidade para todos os níveis do Sistema de Saúde.""")
st.markdown("""Confira os dados deste SINASC referente ao mês de Janeiro de 2019:""")

# Ler e carregar o 
sinasc = pd.read_csv('C:/Users/felip/Desktop/Nova pasta/exercicio 1/SINASC_RO_2019_JAN.csv')
st.write(sinasc)
st.write(sinasc.shape)
csv_filename = "sinasc_ro_2019.csv"  

# Converter 'DTNASC' para formato de data
sinasc['DTNASC'] = pd.to_datetime(sinasc['DTNASC'])

# Barra lateral:
# CSS para mudar a cor de fundo da barra lateral
sidebar_style = """
    <style>
    [data-testid="stSidebar"] {
        background-color: rgb(238, 247, 255);
    }
    </style>
"""
# Injetar o CSS na página
st.markdown(sidebar_style, unsafe_allow_html=True)

# Filtrar a menor e maior data
min_date = sinasc['DTNASC'].min().strftime('%d/%m/%Y') # adequar a data a um formato amigável
max_date = sinasc['DTNASC'].max().strftime('%d/%m/%Y')  

# Criar a barra lateral 
st.sidebar.header("Informações do Dataset")
st.sidebar.markdown(f"📂 **Arquivo**: {csv_filename}")
st.sidebar.markdown(f"📅 **Menor Data**: **{min_date}**")
st.sidebar.markdown(f"📅 **Maior Data**: **{max_date}**")

# Gráficos:
## Quantidade de Nascimentos por Dia
sinasc_agg = sinasc.groupby('DTNASC')['IDADEMAE'].count().reset_index()
sinasc_agg.columns = ['Data de Nascimento', 'Quantidade de Nascimentos']

fig1 = px.line(sinasc_agg, x='Data de Nascimento', y='Quantidade de Nascimentos',
               title='1) Quantidade de Nascimentos por Dia', labels={'Quantidade de Nascimentos': 'Nascimentos'})
st.plotly_chart(fig1)

## Média da Idade da Mãe por Sexo
sinasc_pivot = sinasc.pivot_table(values='IDADEMAE', index='DTNASC', columns='SEXO', aggfunc='mean').reset_index()
fig2 = px.line(sinasc_pivot, x='DTNASC', y=sinasc_pivot.columns[1:],
               title='2) Média da Idade da Mãe por Sexo', labels={'value': 'Média da Idade', 'DTNASC': 'Data'})
st.plotly_chart(fig2)

##  Média do Peso do Bebê por Sexo
sinasc_pivot_peso = sinasc.pivot_table(values='PESO', index='DTNASC', columns='SEXO', aggfunc='mean').reset_index()

fig3 = px.line(sinasc_pivot_peso, x='DTNASC', y=sinasc_pivot_peso.columns[1:],
               title='3) Média do Peso do Bebê por Sexo', labels={'value': 'Peso Médio (g)', 'DTNASC': 'Data'})
st.plotly_chart(fig3)

# -- Notas APGAR
with st.expander("Sobre APGAR"):
    st.markdown("""
 * APGAR: Aparência, Pulso, Gesticulação, Atividade, Respiração.
 * O índice APGAR é um método usado para avaliar a saúde de recém-nascidos logo após o nascimento. Ele é realizado em dois momentos: 1 minuto e 5 minutos após o nascimento.
 * :blue-background[APGAR 1 minuto:] Esta avaliação inicial verifica como o bebê tolerou o processo de nascimento.
 * :blue-background[APGAR 5 minutos:] Esta segunda avaliação verifica como o bebê está se adaptando ao ambiente fora do útero.

Veja também:
* [Escala de Apgar](https://pt.wikipedia.org/wiki/Escala_de_Apgar#:~:text=A%20sigla%20'APGAR'%20%C3%A9%20uma,%2C%20Gesticula%C3%A7%C3%A3o%2C%20Atividade%2C%20Respira%C3%A7%C3%A3o)
""")

##  Média do APGAR1 por Escolaridade da Mãe
sinasc_apgar1 = sinasc.groupby('ESCMAE')['APGAR1'].median().reset_index()

fig4 = px.bar(sinasc_apgar1, x='ESCMAE', y='APGAR1',
              title='4) Média do APGAR1 por Escolaridade da Mãe',
              labels={'ESCMAE': 'Escolaridade', 'APGAR1': 'Média do APGAR1'},
              color='ESCMAE',  # Define cores diferentes por categoria
              color_discrete_sequence=px.colors.qualitative.Set2)  # Paleta de cores
st.plotly_chart(fig4)


## Média do APGAR1 e APGAR5 por Tipo de Gestação
sinasc_apgar_gestacao = sinasc.groupby('GESTACAO')[['APGAR1', 'APGAR5']].mean().reset_index()

fig5 = px.bar(sinasc_apgar_gestacao.melt(id_vars=['GESTACAO'], value_vars=['APGAR1', 'APGAR5']),
              x='GESTACAO', y='value', color='variable', barmode='group',
              title='5) Média do APGAR1 e APGAR5 por Gestação',
              labels={'GESTACAO': 'Gestação', 'value': 'Média', 'variable': 'APGAR'},
              color_discrete_sequence=px.colors.qualitative.Set2)  # Cores diferenciadas
st.plotly_chart(fig5)