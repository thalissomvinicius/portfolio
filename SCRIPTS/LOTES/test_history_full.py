
import sys
import os

# Add backend to path
backend_path = r'c:\Users\thalissom.cruz\Desktop\DASHVALLE\LOTES\novo\backend'
if backend_path not in sys.path:
    sys.path.append(backend_path)

from routes.quitacao import calcular_valor_quitacao

print("Testing calcular_valor_quitacao for Empresa 999, Obra 70100, Q009, L049...")
val, tp, tc, ur, hist, det = calcular_valor_quitacao(999, '70100', '009', '049')

print(f"\nHistórico de Transferências ({len(hist)} vendas):")
for h in hist:
    print(f"\nVenda: {h['numVenda']}")
    print(f"  Cliente: {h['cliente']}")
    print(f"  Valor Pago: R$ {h['valorPago']:,.2f}")
