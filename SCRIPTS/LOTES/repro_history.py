
import asyncio
import sys
import os
from unittest.mock import patch, MagicMock

# Add backend to path FIRST
backend_path = r'c:\Users\thalissom.cruz\Desktop\DASHVALLE\LOTES\novo\backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Mock execute_query
def mock_execute_query(query):
    # Simulate VendaAtual and VendasAnteriores chain
    if "WITH VendaAtual" in query:
        return [
            {"NumVenda": 1945, "Cliente": "ELIETE FERREIRA OGUSHI", "Data_Ven": "2020-01-01", "ValorTot_Ven": 100000, "Origem": "CessaoAnterior"},
            {"NumVenda": 22198, "Cliente": "B R GONCALVES", "Data_Ven": "2024-01-01", "ValorTot_Ven": 200000, "Origem": "VendaAtual"}
        ]
    # Simulate pagamentos map
    if "SELECT R.NumVend_Rec AS NumVenda, SUM" in query:
        return [
            {"NumVenda": 1945, "ValorPago": 38231.08},
            {"NumVenda": 22198, "ValorPago": 5387.92}
        ]
    # Simulate VendaClientes for 1945 (Multiple owners)
    if "VendaClientes" in query and "1945" in query:
        return [
            {"codCliente": 1, "tipo": 0, "participacao": 50.0, "Nome_pes": "ELIETE FERREIRA OGUSHI", "cpf_pes": "111", "rg_pes": "rg1"},
            {"codCliente": 2, "tipo": 0, "participacao": 50.0, "Nome_pes": "OWNER B", "cpf_pes": "222", "rg_pes": "rg2"}
        ]
    # Simulate VendaClientes for 22198 (Single owner)
    if "VendaClientes" in query and "22198" in query:
        return [
            {"codCliente": 3, "tipo": 0, "participacao": 100.0, "Nome_pes": "B R GONCALVES COMERCIO E CONSTRUCOES LTDA", "cpf_pes": "333", "rg_pes": "rg3"}
        ]
    return []

# Patch execute_query in the module
with patch('routes.quitacao.execute_query', side_effect=mock_execute_query):
    from routes.quitacao import calcular_valor_quitacao
    
    def run_test():
        print("Testing history aggregation...")
        # Note: calcular_valor_quitacao is SYNC
        val, tp, tc, ur, hist, det = calcular_valor_quitacao(999, '70100', '009', '049')
        
        print("\nHistory found:")
        for h in hist:
            print(f"Venda: {h['numVenda']} | Cliente: {h['cliente']} | Pago: {h['valorPago']}")
            
        # Verify 1945 has both owners
        v1945 = next(h for h in hist if h['numVenda'] == 1945)
        if "ELIETE FERREIRA OGUSHI (50%)" in v1945['cliente'] and "OWNER B (50%)" in v1945['cliente']:
            print("\nSUCCESS: Venda 1945 has multiple owners with percentages.")
        else:
            print(f"\nFAILURE: Venda 1945 did not aggregate owners correctly. Got: {v1945['cliente']}")

    if __name__ == "__main__":
        run_test()
