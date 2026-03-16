import requests
import json

def test_quitacao():
    print("=== Testando Quitação Venda 22118 ===")
    url = "http://localhost:8000/api/quitacao/dados"
    params = {
        "empresa": 999,
        "obra": "70100",
        "venda": 22118
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            venda = data.get('venda', {})
            lote = data.get('lote', {})
            
            print(f"\nLote: {lote.get('quadra')} - {lote.get('lote')}")
            print(f"Cliente: {data.get('cliente', {}).get('nome')}")
            print(f"Valor Total (Soma Pagamentos): R$ {venda.get('valor'):,.2f}")
            print(f"Último Recebimento: {venda.get('ultimoRecebimento')}")
            
            # Verificar se o valor é maior que 30k (esperado ~38k)
            if venda.get('valor') > 30000:
                print("✅ SUCESSO: Valor reflete histórico de pagamentos!")
            else:
                print("⚠️ AVISO: Valor parece ser apenas da venda atual (esperado > 30k)")
        else:
            print("Erro:", response.text)
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_quitacao()
