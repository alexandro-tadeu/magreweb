import streamlit as st
import streamlit.components.v1 as components
import py3Dmol

def render_pdb(pdb_str):
    view = py3Dmol.view(width=500, height=400)
    view.addModel(pdb_str, "pdb")
    view.setStyle({'cartoon': {'color': 'spectrum'}})
    view.zoomTo()
    components.html(view._make_html(), height=400)

def main():
    st.sidebar.title('Apresentação 3D da proteína')

    # Caixa de texto para o código PDB
    pdb_code = st.sidebar.text_input('Insira o código PDB e pressione Enter:')

    # Seletor de estilo
    style = st.sidebar.selectbox('Selecione o estilo de visualização', ['cartoon', 'stick', 'sphere'])

    if pdb_code:
        def render_mol(pdb, style):
            xyzview = py3Dmol.view(query=f'pdb:{pdb}', width=800, height=500)
            xyzview.setStyle({style: {'color': 'spectrum'}})
            xyzview.setBackgroundColor('white')
            xyzview.zoomTo()
            # Exibir no Streamlit usando components.html
            components.html(xyzview._make_html(), height=500, width=800)

        render_mol(pdb_code, style)
    else:
        st.warning("Por favor, insira um código PDB na caixa de texto acima e pressione Enter.")

if __name__ == "__main__":
    main()
