from database import execute_query
import json

def debug_transfer():
    print("=== Buscando tabelas de Transferência ===")
    query_tables = """
    SELECT TABLE_NAME 
    FROM INFORMATION_SCHEMA.TABLES 
    WHERE TABLE_NAME LIKE '%Transfer%'
    """
    tables = execute_query(query_tables)
    print("Tabelas encontradas:", [t['TABLE_NAME'] for t in tables])

    print("\n=== Inspecionando Venda 22118 ===")
    # Verificar na tabela Vendas e VendasRecebidas se há colunas relevantes
    query_venda = """
    SELECT *
    FROM VendasRecebidas WITH(NOLOCK)
    WHERE Num_VRec = 22118
    """
    venda = execute_query(query_venda)
    
    if not venda:
        print("Venda não encontrada em VendasRecebidas. Buscando em Vendas...")
        query_venda = """
        SELECT *
        FROM Vendas WITH(NOLOCK)
        WHERE Num_Ven = 22118
        """
        venda = execute_query(query_venda)
        
    if venda:
        print("Dados da Venda:")
        row = venda[0]
        # Imprimir campos que possam indicar transferência
        for k, v in row.items():
            if 'transf' in k.lower() or 'anter' in k.lower() or 'origem' in k.lower() or 'venda' in k.lower():
                print(f"{k}: {v}")
                
        # Listar todas as colunas para eu ver se tem algo escondido
        print("\nTodas as colunas:", list(row.keys()))
    else:
        print("Venda 22118 não encontrada.")

    # Tentar achar a tabela de transferencias e consultar por essa venda
    if any('Transferencias' in t['TABLE_NAME'] for t in tables):
        print("\n=== Consultando Tabela Transferencias (chute) ===")
        # Assumindo que possa ter o número da venda nova ou antiga
        try:
            query_transf = """
            SELECT * FROM Transferencias 
            WHERE NumVenda_Transf = 22118 OR NumVendaAnt_Transf = 22118
            """
            transf = execute_query(query_transf)
            print("Resultado Transferencias:", transf)
        except Exception as e:
            print(f"Erro ao consultar Transferencias: {e}")

if __name__ == "__main__":
    debug_transfer()
