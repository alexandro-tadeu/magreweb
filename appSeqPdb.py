import requests
import streamlit as st

def obter_codigo_fasta(codigo_pdb):
    url = f'https://www.rcsb.org/fasta/entry/{codigo_pdb}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Lança exceção para códigos de erro HTTP
        return response.text.splitlines()
    except requests.exceptions.HTTPError as e:
        st.error(f"Erro HTTP ao obter o código FASTA {codigo_pdb}: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Erro de conexão ao tentar acessar o PDB: {e}")
    return None

def extrair_sequencia_fasta(fasta_lines):
    sequencia = ""
    cadeia_info = ""
    for line in fasta_lines:
        if line.startswith(">"):
            cadeia_info = line.strip()
        else:
            sequencia += line.strip()
    return sequencia, cadeia_info

def obter_cadeia(cadeia_info):
    if "|" in cadeia_info:
        partes = cadeia_info.split("|")
        if len(partes) > 1:
            return partes[1].replace("Chains ", "").strip()
    return "N/A"

def main():
    st.title("Extrator de Sequência de Aminoácidos do PDB")

    codigo_pdb = st.text_input("Insira o código da entrada (por exemplo, 1XQ8):", "").upper()

    if st.button("Buscar Sequência"):
        if codigo_pdb:
            fasta_lines = obter_codigo_fasta(codigo_pdb)

            if fasta_lines:
                sequencia_aminoacidos, cadeia_info = extrair_sequencia_fasta(fasta_lines)

                if sequencia_aminoacidos:
                    cadeia = obter_cadeia(cadeia_info)
                    st.write(f"**Cadeia:** {cadeia}")
                    st.success("Sequência de Aminoácidos:")
                    st.code(sequencia_aminoacidos)
                else:
                    st.warning("Nenhuma sequência de aminoácidos encontrada.")
        else:
            st.warning("Por favor, insira um código PDB.")

if __name__ == "__main__":
    main()
