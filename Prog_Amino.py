import requests

class Atom:
    def __init__(self, line):
        self.atom_name = line[12:16].strip()
        self.res_name = line[17:20].strip()
        self.chain_id = line[21]
        self.res_number = int(line[22:26])
        self.coordinates = (
            float(line[30:38]),
            float(line[38:46]),
            float(line[46:54])
        )

def extrair_sequencia(pdb_lines, chain):
    sequencia = ""
    res_numeros_vistos = set()  # Para não repetir resíduos da mesma posição

    for line in pdb_lines:
        if line.startswith("ATOM") and line[21] == chain:
            atom = Atom(line)
            if atom.res_number not in res_numeros_vistos:
                sequencia += atom.res_name
                res_numeros_vistos.add(atom.res_number)

    return sequencia

def obter_pdb_lines(codigo_pdb):
    url = f'https://files.rcsb.org/view/{codigo_pdb}.pdb'
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.splitlines()
    else:
        raise ValueError(f"Erro ao obter o código PDB {codigo_pdb}. Verifique o código e tente novamente.")

def obter_sequencia_por_cadeia(codigo_pdb, chain='A'):
    pdb_lines = obter_pdb_lines(codigo_pdb)
    return extrair_sequencia(pdb_lines, chain)

# Exemplo de uso
if __name__ == "__main__":
    codigo = input("Insira o código PDB: ").strip().upper()
    cadeia = input("Insira a cadeia (default 'A'): ").strip().upper() or 'A'

    try:
        sequencia = obter_sequencia_por_cadeia(codigo, cadeia)
        print(f"Sequência da cadeia {cadeia} do PDB {codigo}:\n{sequencia}")
    except Exception as e:
        print(str(e))
