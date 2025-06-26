import streamlit as st
import requests
import py3Dmol
import os
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
import Prog_Funcoes1
from pathlib import Path

# Variáveis de controle
graficos_gerados = set()
chain = " "

# Diretórios dinâmicos e seguros
BASE_DIR = Path(os.getenv("MAGRE_BASE_DIR", Path.cwd())) / "arquivos"
PDB_DIR = BASE_DIR / "pdb"
TESTES_DIR = BASE_DIR / "testes"

# Certifique-se de que os diretórios necessários existem
PDB_DIR.mkdir(parents=True, exist_ok=True)
TESTES_DIR.mkdir(parents=True, exist_ok=True)

# Função para baixar o arquivo PDB
def baixa_pdb(codigo_pdb):
    url = f'https://files.rcsb.org/view/{codigo_pdb}.pdb'
    response = requests.get(url)
    if response.status_code == 200:
        st.write("Arquivo PDB baixado com sucesso.")
        return response.text
    else:
        st.warning("Não foi possível baixar o arquivo PDB. Verifique o código.")
        return None

# Função para salvar o arquivo PDB
def salva_pdb(codigo_pdb, conteudo):
    caminho = PDB_DIR / f"{codigo_pdb}.pdb"
    with open(caminho, "w") as f:
        f.write(conteudo)
    return caminho

# Função para processar o arquivo PDB e gerar resultados
def processa_pdb(codigo_pdb, conteudo_pdb):
    global chain
    linhas = conteudo_pdb.splitlines()
    resultado = []
    for line in linhas:
        if len(line) < 1:
            continue
        elif line.startswith("ATOM") and line[21:22] != chain:
            chain = line[21:22]
            resultado = Prog_Funcoes1.movimenta(
                codigo_pdb + ".pdb", linhas, "", chain, codigo_pdb, 1
            )
            resultado = Prog_Funcoes1.avalia_ruido(resultado)
    return resultado

# Função para gerar a visualização da sequência com cores
def exibe_sequencia(resultado):
    st.subheader("Detecção de Agregação")
    agregam_count = 0
    nao_agregam_count = 0

    sequence_elements = []
    for linha in resultado:
        dados = linha.split(";")
        posicao = int(dados[1])
        valor = float(dados[3])
        residuo = dados[2]

        color = "red" if valor > 0.5 else "black"
        tooltip = "Este aminoácido agrega." if valor > 0.5 else "Este aminoácido não agrega."

        span_style = f"color: {color}; font-size: 20px; background-color: #F0F0F0; border: 1px solid #CCCCCC; border-radius: 4px; padding: 2px 6px; margin: 2px"
        sequence_elements.append(
            f'<span style="{span_style}" title="{tooltip}">{residuo}</span>'
        )

        if valor > 0.5:
            agregam_count += 1
        else:
            nao_agregam_count += 1

    sequence_html = " ".join(sequence_elements)
    st.markdown(sequence_html, unsafe_allow_html=True)

    st.subheader("Resumo")
    st.write(f"Número de aminoácidos que agregam: {agregam_count}")
    st.write(f"Número de aminoácidos que não agregam: {nao_agregam_count}")

# Função para gerar o gráfico usando Plotly
def plota_resultado_plotly(resultado, codigo_pdb, chain):
    cor_agregacao = 'red'
    cor_normal = 'black'
    cor_limite_inferior = 'orange'
    cor_limite_superior = 'blue'
    tamanho = len(resultado)

    tabela1 = [[0] * tamanho for _ in range(2)]

    for i, linha in enumerate(resultado):
        tabela = linha.split(";")
        tabela1[0][i] = int(tabela[1])
        tabela1[1][i] = float(tabela[3])

    limite_inferior = 0.2
    limite_superior = 0.8

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tabela1[0], 
        y=tabela1[1], 
        mode='lines+markers',
        line=dict(color=cor_normal), 
        name=f"{codigo_pdb}/{chain}",
        hovertemplate="Resíduo: %{x}<br>Probabilidade: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=[tabela1[0][i] for i in range(tamanho) if tabela1[1][i] >= limite_superior],
        y=[tabela1[1][i] for i in range(tamanho) if tabela1[1][i] >= limite_superior],
        mode='markers',
        marker=dict(color=cor_agregacao, size=10),
        name='Agregação Forte',
        hovertemplate="Resíduo: %{x}<br>Probabilidade: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=[tabela1[0][i] for i in range(tamanho) if tabela1[1][i] <= limite_inferior],
        y=[tabela1[1][i] for i in range(tamanho) if tabela1[1][i] <= limite_inferior],
        mode='markers',
        marker=dict(color=cor_limite_inferior, size=10),
        name='Agregação Fraca',
        hovertemplate="Resíduo: %{x}<br>Probabilidade: %{y}<extra></extra>"
    ))

    fig.add_trace(go.Scatter(
        x=tabela1[0], 
        y=[limite_inferior] * tamanho,
        mode='lines', 
        line=dict(color=cor_limite_inferior, dash='dash'), 
        name='Limite Inferior'
    ))

    fig.add_trace(go.Scatter(
        x=tabela1[0], 
        y=[limite_superior] * tamanho,
        mode='lines', 
        line=dict(color=cor_limite_superior, dash='dash'), 
        name='Limite Superior'
    ))

    fig.add_trace(go.Scatter(
        x=tabela1[0], 
        y=[0.5] * tamanho,
        mode='lines', 
        line=dict(color='green'), 
        name='Limiar'
    ))

    fig.update_layout(
        title=f"Propensão à agregação/{codigo_pdb}-{chain}",
        xaxis=dict(title='Resíduo', showgrid=True, zeroline=True, showline=True),
        yaxis=dict(title='Probabilidade', showgrid=True, zeroline=True, showline=True),
        showlegend=True,
        hovermode='closest'
    )

    st.plotly_chart(fig)
    return fig

# Função principal
def main():
    st.title("Gerador de Gráfico, Detecção de Agregação e Visualização 3D")
    codigo_pdb = st.text_input("Informe o código PDB da proteína:")

    if st.button("Gerar Análise"):
        if not codigo_pdb:
            st.warning("Por favor, insira um código PDB válido.")
            return

        conteudo_pdb = baixa_pdb(codigo_pdb)
        if conteudo_pdb:
            caminho_pdb = salva_pdb(codigo_pdb, conteudo_pdb)
            resultado = processa_pdb(codigo_pdb, conteudo_pdb)
            exibe_sequencia(resultado)
            plota_resultado_plotly(resultado, codigo_pdb, chain)

if __name__ == "__main__":
    main()
