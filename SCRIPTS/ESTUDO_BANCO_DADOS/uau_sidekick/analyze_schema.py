import json
import os

schema_path = r'c:\Users\thalissom.cruz\Desktop\PORTIFOLIO\SCRIPTS\ESTUDO_BANCO_DADOS\schema.json'

with open(schema_path, 'r', encoding='utf-8') as f:
    schema = json.load(f)

print(f"Total tables: {len(schema)}")

# Search for tables with "End" in name
end_tables = [t for t in schema if 'END' in t.upper()]
print(f"\nAddress related tables: {end_tables}")

# Search for columns in Pessoas
if 'Pessoas' in schema:
    print("\nPessoas columns:")
    for col in schema['Pessoas']['columns']:
        print(f"  {col['name']}")
else:
    # Try case variants
    pessoas_key = next((k for k in schema if k.lower() == 'pessoas'), None)
    if pessoas_key:
        print(f"\n{pessoas_key} columns:")
        for col in schema[pessoas_key]['columns']:
            print(f"  {col['name']}")

# Search for "Estado" or "Civil" in all columns
found_civil = []
for t, data in schema.items():
    for col in data['columns']:
        if 'CIVIL' in col['name'].upper() or 'REGIME' in col['name'].upper():
            found_civil.append(f"{t}.{col['name']}")

print(f"\nCivil/Regime columns: {found_civil[:20]}...")

# Search for "Endereco" or "Logradouro" or "Cep"
found_address = []
for t, data in schema.items():
    for col in data['columns']:
        cname = col['name'].upper()
        if 'CEP' in cname or 'LOGRADOURO' in cname or 'BAIRRO' in cname:
            found_address.append(f"{t}.{col['name']}")

print(f"\nAddress related columns: {found_address[:20]}...")
