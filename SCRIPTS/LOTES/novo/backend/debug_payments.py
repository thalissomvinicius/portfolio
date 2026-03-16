from database import execute_query

def debug_payments():
    print("=== Verificando Pagamentos para o Histórico do Lote ===")
    
    # Lista de vendas encontradas anteriormente para Quadra G Lote 007
    vendas = [602, 1013, 20817, 20918, 21396, 21682, 22003, 22118]
    empresa = 999
    obra = '70100'
    
    total_geral = 0
    
    for v in vendas:
        query_pagos = f"""
        SELECT COUNT(*) as Qtd, ISNULL(SUM(Valor_Rec + ValorConf_Rec), 0) as TotalPago
        FROM Recebidas WITH(NOLOCK)
        WHERE Empresa_Rec = {empresa}
          AND Obra_Rec = '{obra}'
          AND NumVend_Rec = {v}
        """
        res = execute_query(query_pagos)
        if res:
            qtd = res[0]['Qtd']
            total = res[0]['TotalPago']
            print(f"Venda {v}: {qtd} pagamentos, Total: R$ {total:,.2f}")
            total_geral += float(total)
            
    print(f"\nTotal Geral de Todas as Vendas: R$ {total_geral:,.2f}")

if __name__ == "__main__":
    debug_payments()
