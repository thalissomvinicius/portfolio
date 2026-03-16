import pyodbc
import os
import json

# Connection settings (reusing details found in app.py)
SERVER = 'DCWBD11\\VALLEPRIME_PRD'
DATABASE = 'UAU-VALLEPRIME'
UID = 'consultasBD'
PWD = 'V@lle#2021'

connection_string = f"Driver={{SQL Server}};Server={SERVER};Database={DATABASE};UID={UID};PWD={PWD};"

def get_tables(cursor):
    """Returns a list of all user tables in the database."""
    query = "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME"
    cursor.execute(query)
    return [row.TABLE_NAME for row in cursor.fetchall()]

def get_columns(cursor, table_name):
    """Returns detailed column information for a given table."""
    query = f"""
    SELECT 
        COLUMN_NAME, 
        DATA_TYPE, 
        CHARACTER_MAXIMUM_LENGTH, 
        IS_NULLABLE, 
        COLUMN_DEFAULT
    FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME = ?
    ORDER BY ORDINAL_POSITION
    """
    cursor.execute(query, (table_name,))
    columns = []
    for row in cursor.fetchall():
        columns.append({
            "name": row.COLUMN_NAME,
            "type": row.DATA_TYPE,
            "length": row.CHARACTER_MAXIMUM_LENGTH,
            "nullable": row.IS_NULLABLE,
            "default": row.COLUMN_DEFAULT
        })
    return columns

def get_primary_keys(cursor, table_name):
    """Returns a list of primary key columns for a table."""
    query = """
    SELECT COLUMN_NAME
    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
    WHERE OBJECTPROPERTY(OBJECT_ID(CONSTRAINT_SCHEMA + '.' + CONSTRAINT_NAME), 'IsPrimaryKey') = 1
    AND TABLE_NAME = ?
    """
    cursor.execute(query, (table_name,))
    return [row.COLUMN_NAME for row in cursor.fetchall()]

def main():
    print(f"Connecting to {SERVER}/{DATABASE}...")
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        tables = get_tables(cursor)
        print(f"Found {len(tables)} tables.")
        
        schema = {}
        report_lines = ["# Database Schema Report\n"]
        report_lines.append(f"- **Server:** {SERVER}")
        report_lines.append(f"- **Database:** {DATABASE}\n")
        report_lines.append("## Table Index\n")
        
        for table in tables:
            report_lines.append(f"- [{table}](#{table.lower()})")
            
        report_lines.append("\n---\n")
        
        for i, table in enumerate(tables):
            print(f"Processing table {i+1}/{len(tables)}: {table}")
            columns = get_columns(cursor, table)
            pk = get_primary_keys(cursor, table)
            
            schema[table] = {
                "columns": columns,
                "primary_keys": pk
            }
            
            report_lines.append(f"### {table}")
            report_lines.append("| Column | Type | Max Len | Nullable | Default | PK |")
            report_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            for col in columns:
                is_pk = "Yes" if col['name'] in pk else ""
                report_lines.append(f"| {col['name']} | {col['type']} | {col['length'] or ''} | {col['nullable']} | {col['default'] or ''} | {is_pk} |")
            report_lines.append("\n")
            
            # Stop after 20 tables to avoid massive file if database is huge, 
            # or let it run but be careful. Given the task "study as much as possible", 
            # I'll let it run but maybe limit for initial analysis if needed.
            # Actually, I'll export ALL but keep the report concise.
            
        # Write report
        report_path = os.path.join(os.path.dirname(__file__), 'schema_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(report_lines))
            
        # Write JSON for future tools
        json_path = os.path.join(os.path.dirname(__file__), 'schema.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=4)
            
        print(f"Analysis complete. Report saved to {report_path}")
        
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
