import streamlit as st
import requests
import py3Dmol
from pathlib import Path
import os

# Diretório base dinâmico para uso futuro (cache, logs, etc)
BASE_DIR = Path(os.getenv("MAGRE_BASE_DIR", Path.cwd())) / "arquivos"
BASE_DIR.mkdir(parents=True, exist_ok=True)

def exibir_estrutura_3d(codigo_pdb, resn_especifico=None, resi_especifico=None, estilo='cartoon'):
    url = f'https://files.rcsb.org/view/{codigo_pdb}.pdb'
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Erro ao carregar o arquivo PDB para o código {codigo_pdb}")
            return
        
        pdb_data = response.text

        residues = []
        for line in pdb_data.splitlines():
            if line.startswith("ATOM"):
                resn = line[17:20].strip()
                resi = int(line[22:26].strip())
                chain = line[21:22].strip()
                if (resn, resi, chain) not in residues:
                    residues.append((resn, resi, chain))
        
        if resn_especifico or resi_especifico:
            residues = [
                (resn, resi, chain)
                for (resn, resi, chain) in residues
                if (not resn_especifico or resn == resn_especifico)
                and (not resi_especifico or resi == resi_especifico)
            ]

        viewer = py3Dmol.view(width=800, height=600)
        viewer.addModel(pdb_data, "pdb")

        if estilo == 'cartoon':
            viewer.setStyle({'cartoon': {'color': 'spectrum'}})
        elif estilo == 'stick':
            viewer.setStyle({'stick': {'colorscheme': 'element'}})
        elif estilo == 'sphere':
            viewer.setStyle({'sphere': {'scale': 0.3, 'colorscheme': 'element'}})
        
        for resn, resi, chain in residues:
            viewer.addResLabels({'resi': str(resi), 'resn': resn, 'chain': chain},
                                {'fontColor': 'white', 'backgroundColor': 'black'})
        
        viewer.zoomTo()
        viewer.setBackgroundColor('white')

        viewer_html = viewer._make_html()
        st.components.v1.html(viewer_html, height=600)

    except Exception as e:
        st.error(f"Erro ao exibir a estrutura 3D: {e}")

def main():
    st.title("Visualização de Estrutura 3D com Rótulos para Resíduos Específicos")

    codigo_pdb = st.text_input("Informe o código PDB da proteína:")

    opcao_residuo = st.radio(
        "Escolha a opção de visualização:",
        ("Todos os resíduos", "Resíduo específico pelo número", "Resíduo específico pelo nome")
    )

    resn_especifico = None
    resi_especifico = None
    if opcao_residuo == "Resíduo específico pelo número":
        resi_input = st.text_input("Digite somente o número do resíduo que deseja visualizar (ex: 45):")
        if resi_input:
            try:
                resi_especifico = int(resi_input)
            except ValueError:
                st.warning("Por favor, insira um número válido para o resíduo.")
    elif opcao_residuo == "Resíduo específico pelo nome":
        resn_input = st.text_input("Digite o nome do resíduo que deseja visualizar (ex: ALA):")
        if resn_input:
            resn_especifico = resn_input.strip().upper()
    
    estilo = st.sidebar.selectbox('Selecione o estilo de visualização', ['cartoon', 'stick', 'sphere'])

    if st.button("Gerar Estrutura 3D"):
        if not codigo_pdb:
            st.warning("Por favor, insira um código PDB válido.")
            return

        st.write(f"Código Solicitado: {codigo_pdb}")
        if opcao_residuo == "Resíduo específico pelo número" and resi_especifico:
            st.write(f"Resíduo Selecionado: {resi_especifico}")
        elif opcao_residuo == "Resíduo específico pelo nome" and resn_especifico:
            st.write(f"Resíduo Selecionado: {resn_especifico}")
        else:
            st.write("Exibindo todos os resíduos.")

        exibir_estrutura_3d(codigo_pdb, resn_especifico, resi_especifico, estilo)

if __name__ == '__main__':
    main()
