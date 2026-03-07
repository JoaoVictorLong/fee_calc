#!/usr/bin/env python3
"""
Display interativo para monitorar Fees e Impermanent Loss
Streamlit app com visualização em tempo real
"""

import streamlit as st
import requests
import time
from datetime import datetime

POSITION_ID = 5303576

st.set_page_config(
    page_title="Fee Calc Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
    .big-font {
        font-size: 3rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
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
        st.error(f"Erro ao buscar dados: {e}")
    
    return None


@st.cache_data(ttl=60)
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
        st.error(f"Erro ao buscar câmbio: {e}")
    
    return None


def main():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("💰 Fee Calc Dashboard")
        st.markdown("*Monitorando Posição Uniswap V3 no Arbitrum*")
    
    with col2:
        if st.button("🔄 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Buscar dados
    with st.spinner("Carregando dados..."):
        data = get_performance_metrics()
        usd_brl = get_exchange_rate()
    
    if not data or not usd_brl:
        st.error("❌ Erro ao carregar dados. Tente novamente.")
        return
    
    # Extrair dados
    performance = data.get("performance", {})
    hodl = performance.get("hodl", {})
    
    fees_value_usd = float(data.get('fees_value', 0))
    fees_value_brl = fees_value_usd * usd_brl
    
    il_usd = float(hodl.get('il', 0))
    il_brl = il_usd * usd_brl
    
    total_pnl_usd = fees_value_usd + il_usd
    total_pnl_brl = total_pnl_usd * usd_brl
    
    # Info bar
    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.metric("Posição ID", POSITION_ID)
    with info_col2:
        st.metric("Taxa USD/BRL", f"R$ {usd_brl:.2f}")
    with info_col3:
        st.metric("Atualizado", datetime.now().strftime("%H:%M:%S"))
    
    st.divider()
    
    # Cards principais - Fees e IL
    col1, col2, col3 = st.columns(3)
    
    # Fees Coletadas
    with col1:
        st.markdown("### 💵 Fees Coletadas")
        st.markdown(f"<div style='text-align: center'><p style='font-size: 2.5rem; color: #2ecc71; font-weight: bold;'>${fees_value_usd:.2f}</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'><p style='font-size: 1.5rem; color: #27ae60;'>R$ {fees_value_brl:.2f}</p></div>", unsafe_allow_html=True)
    
    # Impermanent Loss
    with col2:
        st.markdown("### ⚠️  Impermanent Loss")
        color = "#e74c3c" if il_usd < 0 else "#2ecc71"
        st.markdown(f"<div style='text-align: center'><p style='font-size: 2.5rem; color: {color}; font-weight: bold;'>${il_usd:.2f}</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'><p style='font-size: 1.5rem; color: {color};'>R$ {il_brl:.2f}</p></div>", unsafe_allow_html=True)
    
    # Total PnL
    with col3:
        st.markdown("### 📊 Total PnL")
        color = "#2ecc71" if total_pnl_usd >= 0 else "#e74c3c"
        st.markdown(f"<div style='text-align: center'><p style='font-size: 2.5rem; color: {color}; font-weight: bold;'>${total_pnl_usd:.2f}</p></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center;'><p style='font-size: 1.5rem; color: {color};'>R$ {total_pnl_brl:.2f}</p></div>", unsafe_allow_html=True)
    
    st.divider()
    
    # Detalhes expandíveis
    with st.expander("📈 Detalhes Completos de Performance"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Se tivesse feito HODL (mantido):")
            hodl_pnl_usd = float(hodl.get('pnl', 0))
            hodl_pnl_brl = hodl_pnl_usd * usd_brl
            hodl_roi = float(hodl.get('roi', 0)) * 100
            hodl_apr = float(hodl.get('apr', 0))
            
            st.metric("PnL (USD)", f"${hodl_pnl_usd:.2f}")
            st.metric("PnL (BRL)", f"R$ {hodl_pnl_brl:.2f}")
            st.metric("ROI", f"{hodl_roi:.2f}%")
            st.metric("APR", f"{hodl_apr:.2f}%")
        
        with col2:
            st.subheader("Detalhes da Posição:")
            underlying_usd = float(data.get('underlying_value', 0))
            underlying_brl = underlying_usd * usd_brl
            in_range = "✅ Sim" if data.get('in_range') else "❌ Não"
            age = float(data.get('age', 0))
            
            st.metric("Valor Underlying (USD)", f"${underlying_usd:.2f}")
            st.metric("Valor Underlying (BRL)", f"R$ {underlying_brl:.2f}")
            st.metric("In Range", in_range)
            st.metric("Age (dias)", f"{age:.2f}")
        
        # Tokens
        st.subheader("🪙 Tokens na Posição")
        tokens = data.get("tokens", {})
        
        token_cols = st.columns(len(tokens))
        for idx, (addr, token_info) in enumerate(tokens.items()):
            with token_cols[idx]:
                symbol = token_info.get("symbol", "N/A")
                price = float(token_info.get("price", 0))
                st.metric(symbol, f"${price:.2f}")
    
    # Footer com informações
    st.divider()
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.caption("💡 Fees: Ganho com transações")
    with footer_col2:
        st.caption("⚠️  IL: Perdas por mudanças de preço")
    with footer_col3:
        st.caption("📊 PnL: Resultado líquido (Fees - IL)")
    
    # Auto-refresh a cada 60 segundos
    st.markdown("""
    <script>
        setTimeout(function() {
            window.location.reload();
        }, 60000);
    </script>
    """, unsafe_allow_html=True)
    
    st.caption("🔄 Auto-refresh a cada 60 segundos | Última atualização: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


if __name__ == "__main__":
    main()
