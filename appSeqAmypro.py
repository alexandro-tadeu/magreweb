import requests
import streamlit as st

def obter_sequencia_amypro(codigo_entry):
    url = f"http://browsehappy.com/{codigo_entry}.fasta"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip()
    else:
        st.error(f"Erro ao obter dados do AmyPro. Status: {response.status_code}")
        return None

def extrair_informacoes(sequencia):
    linhas = sequencia.split("\n")
    if len(linhas) < 2:
        return {}

    # Linha com as informações, geralmente começa com >
    linha_info = linhas[0].strip()
    seq_aminoacidos = "".join(linhas[1:]).strip()  # junta todas as linhas após a primeira, caso haja múltiplas

    dados = {}

    # Extrair código (string após >)
    if linha_info.startswith(">"):
        dados["codigo"] = linha_info[1:].split()[0]  # primeiro token após '>'
    else:
        dados["codigo"] = "N/A"

    # Tentar extrair nome da proteína e organismo (normalmente segundo token)
    tokens = linha_info[1:].split()
    if len(tokens) > 1:
        dados["nome_proteina"] = tokens[1]
    else:
        dados["nome_proteina"] = "N/A"

    # Extrair pares chave=valor da linha (por exemplo pdb=XXXX, regions={...})
    for token in tokens[2:]:  # pula código e nome já tratados
        if "=" in token:
            chave, valor = token.split("=", 1)
            valor = valor.strip()

            # Tratar regiões que podem vir com chaves {} e múltiplos valores
            if chave == "regions":
                # Exemplo: regions={1-5,10-20}
                if valor.startswith("{") and valor.endswith("}"):
                    regioes = valor[1:-1].split(",")
                    regioes = [r.strip() for r in regioes if r.strip()]
                    dados["regioes"] = regioes
                else:
                    dados["regioes"] = [valor]
            else:
                dados[chave] = valor
        else:
            # Se não tem '=', pode ser flag
            dados[token] = True

    dados["sequencia_aminoacidos"] = seq_aminoacidos
    dados["codigo_pdb"] = dados.get("pdb", "N/A")
    return dados

def main():
    st.title("Extrator de Sequência de Aminoácidos do AmyPro")

    codigo_entry = st.text_input("Insira o código da entrada (por exemplo, AP00015):", "").upper()

    if st.button("Buscar Sequência"):
        if not codigo_entry:
            st.warning("Por favor, insira um código de entrada.")
            return

        sequencia = obter_sequencia_amypro(codigo_entry)
        if not sequencia:
            st.warning("Nenhuma sequência encontrada.")
            return

        dados = extrair_informacoes(sequencia)
        if not dados:
            st.warning("Falha ao extrair informações da sequência.")
            return

        st.write(f"**Código:** {dados.get('codigo', 'N/A')}")
        st.write(f"**Nome da Proteína:** {dados.get('nome_proteina', 'N/A')}")
        st.write(f"**Código PDB:** {dados.get('codigo_pdb', 'N/A')}")

        regioes = dados.get("regioes", [])
        if regioes:
            regioes_formatadas = ", ".join(regioes)
            st.write(f"**Regiões de Agregação:** {regioes_formatadas}")
        else:
            st.write("**Regiões de Agregação:** N/A")

        st.success("Sequência de Aminoácidos:")
        st.code(dados.get("sequencia_aminoacidos", ""))

if __name__ == "__main__":
    main()
