import sys
import os

# Add the current directory to path to import quitacao
sys.path.append(os.getcwd())

from routes.quitacao import get_clientes_venda, get_estado_civil_label, get_regime_casamento_label

def debug_quitacao_data():
    empresa = 999
    obra = '70100'
    num_venda = 2
    
    print(f"=== Debugging get_clientes_venda for Venda {num_venda} ===")
    clientes = get_clientes_venda(empresa, obra, num_venda)
    print(f"Found {len(clientes)} clients.")
    
    for i, cli in enumerate(clientes):
        print(f"\nClient {i+1}:")
        print(f" - Nome: {cli.get('nome')}")
        print(f" - Bairro: '{cli.get('bairro')}'")
        print(f" - Cidade: '{cli.get('cidade')}'")
        print(f" - Endereco: '{cli.get('endereco')}'")
        print(f" - UF: '{cli.get('uf')}'")
        print(f" - RG: '{cli.get('rg')}'")
        print(f" - EstCivil: '{cli.get('estadoCivil')}'")
        print(f" - Regime: '{cli.get('regimeCasamento')}'")

if __name__ == "__main__":
    debug_quitacao_data()
