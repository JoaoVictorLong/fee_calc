#!/usr/bin/env python3
"""
Script para buscar Impermanent Loss (IL) e Fees Collected.
Use -a ou --all para ver todas as informações de performance.
"""

import requests
import argparse
import sys

POSITION_ID = 5303576

def get_performance_metrics():
    """
    Busca métricas de performance incluindo Impermanent Loss.
    """
    url = f"https://api.revert.finance/v1/positions/arbitrum/uniswapv3/{POSITION_ID}"
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200 and response.json().get("success"):
            data = response.json().get("data", {})
            return data
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
    
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
    Função principal com suporte a argumentos.
    """
    parser = argparse.ArgumentParser(
        description="Extrai Fees e Impermanent Loss do Revert Finance"
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Mostra todas as informações de performance"
    )
    
    args = parser.parse_args()
    
    print(f"Buscando dados da posição {POSITION_ID}...\n")
    
    data = get_performance_metrics()
    
    if not data:
        print("✗ Não foi possível obter dados")
        sys.exit(1)
    
    usd_brl = get_exchange_rate()
    if not usd_brl:
        print("✗ Não foi possível obter câmbio USD-BRL")
        sys.exit(1)
    
    if args.all:
        show_all_metrics(data, usd_brl)
    else:
        show_summary(data, usd_brl)


def show_summary(data, usd_brl):
    """
    Mostra apenas Fees Coletadas e Impermanent Loss.
    """
    performance = data.get("performance", {})
    hodl = performance.get("hodl", {})
    
    # Fees
    fees_value_usd = float(data.get('fees_value', 0))
    fees_value_brl = fees_value_usd * usd_brl
    
    # IL
    il_usd = float(hodl.get('il', 0))
    il_brl = il_usd * usd_brl
    
    print("="*50)
    print("💵 FEES COLLECTED")
    print("="*50)
    print(f"USD: ${fees_value_usd:.2f}")
    print(f"BRL: R${fees_value_brl:.2f}")
    
    print("\n" + "="*50)
    print("⚠️  IMPERMANENT LOSS")
    print("="*50)
    print(f"USD: ${il_usd:.2f}")
    print(f"BRL: R${il_brl:.2f}")
    print("\n(Use -a ou --all para ver mais detalhes)")


def show_all_metrics(data, usd_brl):
    """
    Mostra todas as métricas de performance.
    """
    performance = data.get("performance", {})
    
    print("="*60)
    print("MÉTRICAS DE PERFORMANCE")
    print("="*60)
    
    # HODL (se tivesse apenas mantido os tokens)
    hodl = performance.get("hodl", {})
    print("\n📊 IF YOU HELD (HODL):")
    print(f"  PnL USD: ${float(hodl.get('pnl', 0)):.2f}")
    print(f"  PnL BRL: R${float(hodl.get('pnl', 0)) * usd_brl:.2f}")
    print(f"  ROI: {float(hodl.get('roi', 0))*100:.2f}%")
    print(f"  APR: {float(hodl.get('apr', 0)):.2f}%")
    
    # IL (Impermanent Loss / Divergent Loss)
    il_usd = float(hodl.get('il', 0))
    il_brl = il_usd * usd_brl
    print(f"\n⚠️  IMPERMANENT LOSS (IL/Divergent Loss):")
    print(f"  IL USD: ${il_usd:.2f}")
    print(f"  IL BRL: R${il_brl:.2f}")
    
    # Fees ganho
    fee_apr = float(hodl.get('fee_apr', 0))
    print(f"\n💰 FEES APR: {fee_apr:.2f}%")
    
    # Fees value
    fees_value_usd = float(data.get('fees_value', 0))
    fees_value_brl = fees_value_usd * usd_brl
    print(f"💵 Fees Collected (USD): ${fees_value_usd:.2f}")
    print(f"💵 Fees Collected (BRL): R${fees_value_brl:.2f}")
    
    # Total PnL (fees - IL)
    total_pnl_usd = fees_value_usd + il_usd
    total_pnl_brl = total_pnl_usd * usd_brl
    
    print("\n" + "="*60)
    print("RESUMO TOTAL")
    print("="*60)
    print(f"Total PnL (Fees - IL) USD: ${total_pnl_usd:.2f}")
    print(f"Total PnL (Fees - IL) BRL: R${total_pnl_brl:.2f}")
    print("="*60)
    
    # Posição detalhes
    print("\n📍 POSIÇÃO DETALHES:")
    print(f"  Underlying Value (USD): ${float(data.get('underlying_value', 0)):.2f}")
    print(f"  Underlying Value (BRL): R${float(data.get('underlying_value', 0)) * usd_brl:.2f}")
    print(f"  In Range: {'✓ Sim' if data.get('in_range') else '✗ Não'}")
    print(f"  Age (dias): {float(data.get('age', 0)):.2f}")
    
    # Token information
    tokens = data.get("tokens", {})
    print("\n🪙 TOKENS:")
    for addr, token_info in tokens.items():
        symbol = token_info.get("symbol")
        price = token_info.get("price")
        print(f"  {symbol}: ${float(price):.2f}")


if __name__ == "__main__":
    main()
