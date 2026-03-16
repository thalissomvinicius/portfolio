
import sys
import os

# Add backend to path
backend_path = r'c:\Users\thalissom.cruz\Desktop\DASHVALLE\LOTES\novo\backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

from routes.quitacao import get_clientes_venda

# Test with Venda 1945
print("Testing get_clientes_venda for Venda 1945...")
clientes = get_clientes_venda(empresa=999, obra='70100', num_venda=1945)

print(f"\nTotal clientes found: {len(clientes)}")
for c in clientes:
    print(f"  - Tipo: {c['tipo']}, Nome: {c['nome']}, Participação: {c['participacao']}%")

# Filter titulares
titulares = [c for c in clientes if c.get('tipo') == 0]
print(f"\nTotal titulares (tipo=0): {len(titulares)}")

# Format as it would appear in history
if titulares:
    partes = []
    for t in titulares:
        perc = t.get('participacao', 0)
        if perc > 0:
            partes.append(f"{t['nome'].upper()} ({perc:.0f}%)")
        else:
            partes.append(t['nome'].upper())
    cliente_desc = ", ".join(partes)
    print(f"\nFormatted for history table: {cliente_desc}")
