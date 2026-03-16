"""
Script para explorar e documentar a estrutura do banco de dados SQL Server
"""

import pyodbc
import json
from datetime import datetime

# Database configuration  
DB_CONFIG = {
    "driver": "SQL Server",
    "server": "DCWBD11\\VALLEPRIME_PRD",
    "database": "UAU-VALLEPRIME",
    "uid": "consultasBD",
    "pwd": "V@lle#2021",
    "timeout": 60
}

def get_connection():
    conn_str = (
        f"Driver={{{DB_CONFIG['driver']}}};"
        f"Server={DB_CONFIG['server']};"
        f"Database={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['uid']};"
        f"PWD={DB_CONFIG['pwd']};"
        f"Timeout={DB_CONFIG['timeout']};"
    )
    return pyodbc.connect(conn_str)

def get_all_tables(conn):
    """Lista todas as tabelas do banco"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    return [row[0] for row in cursor.fetchall()]

def get_table_columns(conn, table_name):
    """Retorna colunas de uma tabela"""
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE,
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
    """, (table_name,))
    
    columns = []
    for row in cursor.fetchall():
        columns.append({
            'name': row[0],
            'type': row[1],
            'max_length': row[2],
            'nullable': row[3],
            'default': row[4]
        })
    return columns

def get_table_row_count(conn, table_name):
    """Conta registros na tabela"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM [{table_name}] WITH(NOLOCK)")
        return cursor.fetchone()[0]
    except:
        return "N/A"

def get_primary_keys(conn, table_name):
    """Retorna chaves primárias"""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COLUMN_NAME
        FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
        WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + QUOTENAME(CONSTRAINT_NAME)), 'IsPrimaryKey') = 1
        AND TABLE_NAME = ?
    """, (table_name,))
    return [row[0] for row in cursor.fetchall()]

def main():
    print("=" * 60)
    print("  ESTUDO DO BANCO DE DADOS UAU-VALLEPRIME")
    print("=" * 60)
    print(f"\nData: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Servidor: {DB_CONFIG['server']}")
    print(f"Database: {DB_CONFIG['database']}")
    print("-" * 60)
    
    conn = get_connection()
    
    # Listar todas as tabelas
    tables = get_all_tables(conn)
    print(f"\n📊 Total de tabelas encontradas: {len(tables)}\n")
    
    # Agrupar tabelas por prefixo comum
    table_groups = {}
    for t in tables:
        # Tentar identificar prefixo
        prefix = t.split('_')[0] if '_' in t else t[:3]
        if prefix not in table_groups:
            table_groups[prefix] = []
        table_groups[prefix].append(t)
    
    # Listar grupos
    print("📁 Tabelas agrupadas por prefixo:")
    for prefix, group_tables in sorted(table_groups.items()):
        print(f"  {prefix}: {len(group_tables)} tabela(s)")
    
    # Detalhar tabelas principais (mais usadas no sistema)
    important_tables = [
        'Vendas', 'Pessoas', 'ContasReceber', 'Recebidas', 
        'UnidadePer', 'Boleto', 'ItensVenda', 'RecebePgto',
        'RecebePgtoDiv', 'Depositos', 'Extrato', 'Empresa',
        'Obras', 'Produtos', 'BoletoMov', 'Parcelas'
    ]
    
    results = {
        'generated_at': datetime.now().isoformat(),
        'server': DB_CONFIG['server'],
        'database': DB_CONFIG['database'],
        'total_tables': len(tables),
        'all_tables': tables,
        'table_groups': table_groups,
        'detailed_tables': {}
    }
    
    print("\n" + "=" * 60)
    print("  DETALHES DAS TABELAS PRINCIPAIS")
    print("=" * 60)
    
    for table in important_tables:
        if table in tables:
            print(f"\n📋 {table}")
            print("-" * 40)
            
            columns = get_table_columns(conn, table)
            row_count = get_table_row_count(conn, table)
            pks = get_primary_keys(conn, table)
            
            print(f"   Registros: {row_count:,}" if isinstance(row_count, int) else f"   Registros: {row_count}")
            print(f"   Colunas: {len(columns)}")
            print(f"   PKs: {', '.join(pks) if pks else 'N/A'}")
            print("\n   Estrutura:")
            
            for col in columns[:15]:  # Limitar a 15 colunas para não poluir
                pk_marker = " 🔑" if col['name'] in pks else ""
                type_str = col['type']
                if col['max_length']:
                    type_str += f"({col['max_length']})"
                null_str = "NULL" if col['nullable'] == 'YES' else "NOT NULL"
                print(f"      {col['name']:<30} {type_str:<20} {null_str}{pk_marker}")
            
            if len(columns) > 15:
                print(f"      ... e mais {len(columns) - 15} colunas")
            
            results['detailed_tables'][table] = {
                'row_count': row_count if isinstance(row_count, int) else 0,
                'columns': columns,
                'primary_keys': pks
            }
    
    # Salvar JSON com resultados
    with open('database_schema.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    
    print("\n" + "=" * 60)
    print("  RESUMO SALVO EM: database_schema.json")
    print("=" * 60)
    
    conn.close()

if __name__ == "__main__":
    main()
