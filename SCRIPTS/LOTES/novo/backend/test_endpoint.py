"""
Script para testar o endpoint via HTTP
"""
import urllib.request
import json

url = "http://localhost:8000/api/corretores/stats?empresa=28&obra=70100&data_inicio=2025-12-01&data_fim=2025-12-27"

print(f"Testando endpoint: {url}", flush=True)
print("=" * 80, flush=True)

try:
    with urllib.request.urlopen(url) as response:
        data = json.loads(response.read().decode())
        
        print(f"Total de corretores: {len(data['corretores'])}", flush=True)
        print(f"Total de vendas: {data['totais']['totalVendas']}", flush=True)
        print(f"Valor total: R$ {data['totais']['valorTotal']:,.2f}", flush=True)
        print("-" * 80, flush=True)
        print("Top 10 corretores:", flush=True)
        for i, c in enumerate(data['corretores'][:10], 1):
            print(f"{i}. {c['corretor']}: {c['totalVendas']} vendas - R$ {c['valorTotal']:,.2f}", flush=True)
except Exception as e:
    print(f"ERRO: {e}", flush=True)
