#!/usr/bin/env python3
"""
Script rápido para buscar o valor de fees_value do Revert Finance
e converter para BRL.
"""

import requests

POSITION_ID = 5303576

def get_fees_value():
    """
    Busca o fees_value direto da API do Revert Finance.
    """
    url = f"https://api.revert.finance/v1/positions/arbitrum/uniswapv3/{POSITION_ID}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and response.json().get("success"):
            data = response.json().get("data", {})
            fees_value = float(data.get("fees_value", 0))
            return fees_value
    except Exception as e:
        print(f"Erro ao buscar fees_value: {e}")
    
    return None


def get_exchange_rate():
    """
    Obtém a taxa de câmbio USD-BRL atual.
    """
    try:
        response = requests.get(
            "https://economia.awesomeapi.com.br/json/last/USD-BRL"
        )
        if response.status_code == 200:
            usd_brl = float(response.json()["USDBRL"]["bid"])
            return usd_brl
    except Exception as e:
        print(f"Erro ao buscar câmbio: {e}")
    
    return None


def main():
    """
    Função principal.
    """
    print(f"Buscando fees_value da posição {POSITION_ID}...\n")
    
    fees_usd = get_fees_value()
    
    if fees_usd is None:
        print("✗ Não foi possível obter fees_value")
        return
    
    print(f"✓ Fees USD: ${fees_usd:.2f}")
    
    usd_brl = get_exchange_rate()
    
    if usd_brl is None:
        print("✗ Não foi possível obter câmbio USD-BRL")
        return
    
    print(f"✓ Câmbio: 1 USD = R${usd_brl:.2f}")
    
    fees_brl = fees_usd * usd_brl
    
    print("\n" + "="*50)
    print("RESULTADO")
    print("="*50)
    print(f"Fees em USD: ${fees_usd:.2f}")
    print(f"Fees em BRL: R${fees_brl:.2f}")
    print("="*50)


if __name__ == "__main__":
    main()
