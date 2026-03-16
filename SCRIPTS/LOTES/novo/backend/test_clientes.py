from database import execute_query

# Verificar colunas da tabela VendaClientes
cols = execute_query("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'VendaClientes'")
print('Colunas VendaClientes:', [c['COLUMN_NAME'] for c in cols])

# Query completa com CPF
result = execute_query("""
SELECT 
    VC.Cliente_CVen as codCliente,
    VC.Tipo_CVen as tipo,
    P.Nome_pes as nome,
    P.cpf_pes as cpf,
    P.dtnasc_pes as dataNasc
FROM (
   SELECT * FROM VendaClientes WITH(NOLOCK) 
   UNION
   SELECT * FROM VendaRecClientes WITH(NOLOCK) 
) AS VC
INNER JOIN Pessoas P WITH(NOLOCK) 
   ON VC.Cliente_CVen = P.cod_pes 
WHERE VC.Empresa_cven = 999
   AND VC.Num_CVen = 284
   AND VC.Obra_CVen = '70100'
ORDER BY VC.Tipo_CVen
""")

print('\nClientes da venda 284:')
for r in result:
    print(f"  - {r.get('nome')} | CPF: {r.get('cpf')} | Tipo: {r.get('tipo')}")
