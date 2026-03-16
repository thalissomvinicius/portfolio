"""
Script para verificar quais boletos NÃO possuem Status 2 (Recebida)
"""

import sys
sys.path.insert(0, r'c:\Users\thalissom.cruz\Desktop\DASHVALLE\LOTES\novo\backend')

from database import execute_query

# Lista de Nosso Nº a verificar
nosso_numeros = [
    591, 1376, 168, 1432, 1437, 893, 1605, 1611, 1608, 1612, 1602, 1446, 1445, 1401, 331, 1238,
    832, 1593, 1375, 323, 1389, 1626, 1584, 1466, 1701, 1559, 1679, 1558, 1537, 1689, 1013, 1614,
    1741, 1569, 1572, 395, 1061, 1716, 1713, 1709, 1367, 1641, 1652, 1649, 1657, 1662, 1664, 1677,
    1739, 1712, 1647, 1653, 1663, 1669, 1700, 1661, 1671, 1685, 1665, 1667, 1693, 1672, 1683, 1642,
    1742, 1643, 1644, 1623, 1646, 1648, 1535, 1639, 1638, 1640, 1743, 1526, 1650, 1651, 1659, 1660,
    1645, 1658, 1705, 1668, 1676, 1708, 1682, 1704, 1670, 1678, 1692, 1688, 1751, 1746, 1756, 1560,
    1487, 1480, 1534, 1492, 1488, 1489, 1490, 1491, 1478, 1479, 1510, 1513, 1555, 1371, 1557, 1544,
    1373, 1539, 1548, 1552, 1554, 1553, 1575, 1694, 1732, 1730, 1731, 1744, 1417, 1395, 1561, 1697,
    1757, 1531, 1599, 1617, 1523, 1498, 1520, 1518, 1524, 1502, 1521, 1516, 1517, 1522, 1654, 677,
    226, 227, 363, 364, 1752, 1391, 1753, 1754, 1170, 1209, 1158, 1164, 1185, 1269, 1179, 1566,
    1563, 1203, 1259, 1386, 1176
]

# Converter lista para string SQL
nosso_numeros_str = ','.join(str(n) for n in nosso_numeros)

# Query para buscar todos os boletos da lista com seus status
query = f"""
SELECT 
    SeuNum_Bol AS NossoNum,
    Num_Bol AS NumBoleto,
    Banco_Bol AS Banco,
    StatusBanco_Bol AS StatusBanco,
    rac.Status_Rea AS StatusRecebAuto,
    Nome_Pes AS NomeCliente,
    DataVenc_Bol AS DataVencimento,
    ValDoc_Bol AS Valor,
    Empresas.Desc_emp AS Empresa
FROM BoletoConfirmado
INNER JOIN Empresas ON BoletoConfirmado.Empresa_Bol = Empresas.Codigo_emp
LEFT JOIN Pessoas ON Cod_Pes = ClienteVen_Bol
LEFT JOIN (
    SELECT SeuNum_Rea, Banco_Rea, NumBol_Rea, Status_Rea
    FROM RecebAutoConfirmado
    UNION
    SELECT SeuNum_rea, Banco_rea, NumBol_rea, Status_rea
    FROM PropostaRecebAutoConfirmado
) AS rac ON rac.NumBol_Rea = Num_Bol 
         AND rac.SeuNum_Rea = SeuNum_Bol 
         AND rac.Banco_Rea = Banco_Bol
WHERE Empresa_Bol IN (29) 
  AND SeuNum_Bol IN ({nosso_numeros_str})
ORDER BY SeuNum_Bol
"""

print("="*80)
print("VERIFICAÇÃO DE BOLETOS - Status != 2 (Recebida)")
print("="*80)
print(f"Total de Nosso Nº a verificar: {len(nosso_numeros)}")
print("-"*80)

try:
    results = execute_query(query)
    
    # Separar por status
    recebidos = []  # Status 2
    nao_recebidos = []  # Status != 2
    nao_encontrados = set(nosso_numeros)  # Inicializa com todos
    
    for row in results:
        nosso_num = row['NossoNum']
        status = row.get('StatusRecebAuto')
        
        if nosso_num in nao_encontrados:
            nao_encontrados.remove(nosso_num)
        
        if status == 2:
            recebidos.append(row)
        else:
            nao_recebidos.append(row)
    
    # Exibir boletos NÃO recebidos (Status != 2)
    print(f"\n📛 BOLETOS SEM STATUS 2 (NÃO RECEBIDOS): {len(nao_recebidos)}")
    print("-"*80)
    if nao_recebidos:
        print(f"{'NossoNº':<10} {'Status':<10} {'Valor':<15} {'Vencimento':<12} {'Cliente':<40}")
        print("-"*80)
        for row in nao_recebidos:
            nosso = row['NossoNum']
            status = row.get('StatusRecebAuto', 'NULL')
            valor = row.get('Valor', 0) or 0
            venc = row.get('DataVencimento', '')
            venc_str = venc.strftime('%d/%m/%Y') if venc else 'N/A'
            cliente = (row.get('NomeCliente', '') or 'N/A')[:40]
            print(f"{nosso:<10} {str(status):<10} R$ {valor:>10,.2f}  {venc_str:<12} {cliente}")
    else:
        print("Nenhum boleto encontrado sem status 2.")
    
    # Exibir boletos recebidos para conferência
    print(f"\n✅ BOLETOS COM STATUS 2 (RECEBIDOS): {len(recebidos)}")
    print("-"*80)
    
    # Exibir Nosso Nº não encontrados
    if nao_encontrados:
        print(f"\n⚠️ NOSSO Nº NÃO ENCONTRADOS NA BASE (Empresa 29): {len(nao_encontrados)}")
        print("-"*80)
        print(sorted(list(nao_encontrados)))
    
    # Resumo final
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)
    print(f"Total verificado: {len(nosso_numeros)}")
    print(f"Encontrados com Status 2 (Recebidos): {len(recebidos)}")
    print(f"Encontrados sem Status 2 (Não Recebidos): {len(nao_recebidos)}")
    print(f"Não encontrados na Empresa 29: {len(nao_encontrados)}")

except Exception as e:
    print(f"Erro ao executar query: {e}")
    import traceback
    traceback.print_exc()
