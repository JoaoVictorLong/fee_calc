#!/usr/bin/env python3
"""
Aplicação Desktop com Tkinter (mais compatível)
Display elegante para Fees e Impermanent Loss
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
from datetime import datetime

POSITION_ID = 5303576

def get_performance_metrics():
    """Busca métricas de performance incluindo Impermanent Loss."""
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
    """Obtém a taxa de câmbio USD-BRL atual."""
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


def fetch_data_thread(window):
    """Busca dados em thread para não congelar UI."""
    data = get_performance_metrics()
    usd_brl = get_exchange_rate()
    
    if data and usd_brl:
        window.write_event_value('-THREAD-', (data, usd_brl))
    else:
        window.write_event_value('-THREAD-', None)


def create_window():
    """Cria a janela principal."""
    
    header_font = ('Helvetica', 14, 'bold')
    value_font = ('Helvetica', 18, 'bold')
    label_font = ('Helvetica', 10)
    
    layout = [
        # Header
        [
            sg.Text('💰 FEE CALC DASHBOARD', font=('Helvetica', 20, 'bold'), text_color='#2ecc71')
        ],
        [
            sg.Text('Monitorando Posição Uniswap V3 no Arbitrum', font=label_font, text_color='#95a5a6')
        ],
        [sg.HorizontalSeparator()],
        
        # Info bar
        [
            sg.Column([
                [sg.Text(f'Posição ID: {POSITION_ID}', font=label_font)],
                [sg.Text('Taxa USD/BRL: -', font=label_font, key='-EXCHANGE-')]
            ]),
            sg.Column([
                [sg.Text('Atualizado: -', font=label_font, key='-TIME-')]
            ], element_justification='right')
        ],
        
        [sg.HorizontalSeparator()],
        
        # Cards principais
        [
            sg.Column([
                [sg.Text('💵 FEES COLETADAS', font=header_font, text_color='#2ecc71')],
                [sg.Text('$0.00', font=value_font, key='-FEES-USD-', text_color='#2ecc71')],
                [sg.Text('R$ 0.00', font=('Helvetica', 14), key='-FEES-BRL-', text_color='#27ae60')],
            ], vertical_alignment='center', border_width=1, relief=sg.RELIEF_SUNKEN),
            
            sg.Column([
                [sg.Text('⚠️  IMPERMANENT LOSS', font=header_font, text_color='#e74c3c')],
                [sg.Text('$0.00', font=value_font, key='-IL-USD-', text_color='#e74c3c')],
                [sg.Text('R$ 0.00', font=('Helvetica', 14), key='-IL-BRL-', text_color='#c0392b')],
            ], vertical_alignment='center', border_width=1, relief=sg.RELIEF_SUNKEN),
            
            sg.Column([
                [sg.Text('📊 TOTAL PnL', font=header_font, text_color='#3498db')],
                [sg.Text('$0.00', font=value_font, key='-PNL-USD-', text_color='#3498db')],
                [sg.Text('R$ 0.00', font=('Helvetica', 14), key='-PNL-BRL-', text_color='#2980b9')],
            ], vertical_alignment='center', border_width=1, relief=sg.RELIEF_SUNKEN),
        ],
        
        [sg.HorizontalSeparator()],
        
        # Detalhes expandíveis
        [
            sg.Column([
                [sg.Text('📈 SE TIVESSE FEITO HODL', font=header_font, text_color='#f39c12')],
                [sg.Text('PnL USD: $0.00', font=label_font, key='-HODL-PNL-USD-')],
                [sg.Text('PnL BRL: R$ 0.00', font=label_font, key='-HODL-PNL-BRL-')],
                [sg.Text('ROI: 0.00%', font=label_font, key='-HODL-ROI-')],
                [sg.Text('APR: 0.00%', font=label_font, key='-HODL-APR-')],
            ], border_width=1, relief=sg.RELIEF_SUNKEN),
            
            sg.Column([
                [sg.Text('📍 DETALHES DA POSIÇÃO', font=header_font, text_color='#9b59b6')],
                [sg.Text('Valor Underlying USD: $0.00', font=label_font, key='-UNDERLYING-USD-')],
                [sg.Text('Valor Underlying BRL: R$ 0.00', font=label_font, key='-UNDERLYING-BRL-')],
                [sg.Text('In Range: -', font=label_font, key='-IN-RANGE-')],
                [sg.Text('Age (dias): 0.00', font=label_font, key='-AGE-')],
            ], border_width=1, relief=sg.RELIEF_SUNKEN),
        ],
        
        [sg.HorizontalSeparator()],
        
        # Tokens
        [sg.Text('🪙 TOKENS NA POSIÇÃO', font=header_font, text_color='#1abc9c')],
        [sg.Column([[]], key='-TOKENS-', border_width=1, relief=sg.RELIEF_SUNKEN)],
        
        [sg.HorizontalSeparator()],
        
        # Botões
        [
            sg.Button('🔄 Atualizar', size=(15, 1), key='-REFRESH-'),
            sg.Button('❌ Sair', size=(15, 1)),
            sg.Checkbox('Auto-refresh (60s)', default=True, key='-AUTO-REFRESH-'),
        ],
        
        [sg.Text('Status: Carregando...', key='-STATUS-', font=label_font, text_color='#f39c12')],
    ]
    
    return sg.Window('Fee Calc - Desktop App', layout, finalize=True, size=(900, 800))


def update_ui(window, data, usd_brl):
    """Atualiza todos os valores da interface."""
    
    performance = data.get("performance", {})
    hodl = performance.get("hodl", {})
    
    # Calcular valores
    fees_value_usd = float(data.get('fees_value', 0))
    fees_value_brl = fees_value_usd * usd_brl
    
    il_usd = float(hodl.get('il', 0))
    il_brl = il_usd * usd_brl
    
    total_pnl_usd = fees_value_usd + il_usd
    total_pnl_brl = total_pnl_usd * usd_brl
    
    # Custas principais
    window['-EXCHANGE-'].update(f'Taxa USD/BRL: R$ {usd_brl:.2f}')
    window['-TIME-'].update(f'Atualizado: {datetime.now().strftime("%H:%M:%S")}')
    
    window['-FEES-USD-'].update(f'${fees_value_usd:.2f}')
    window['-FEES-BRL-'].update(f'R$ {fees_value_brl:.2f}')
    
    # Cores dinâmicas para IL
    color_il = '#e74c3c' if il_usd < 0 else '#2ecc71'
    window['-IL-USD-'].update(f'${il_usd:.2f}', text_color=color_il)
    window['-IL-BRL-'].update(f'R$ {il_brl:.2f}')
    
    # Core dinàmica para PnL
    color_pnl = '#2ecc71' if total_pnl_usd >= 0 else '#e74c3c'
    window['-PNL-USD-'].update(f'${total_pnl_usd:.2f}', text_color=color_pnl)
    window['-PNL-BRL-'].update(f'R$ {total_pnl_brl:.2f}')
    
    # Detalhes HODL
    hodl_pnl_usd = float(hodl.get('pnl', 0))
    hodl_pnl_brl = hodl_pnl_usd * usd_brl
    hodl_roi = float(hodl.get('roi', 0)) * 100
    hodl_apr = float(hodl.get('apr', 0))
    
    window['-HODL-PNL-USD-'].update(f'PnL USD: ${hodl_pnl_usd:.2f}')
    window['-HODL-PNL-BRL-'].update(f'PnL BRL: R$ {hodl_pnl_brl:.2f}')
    window['-HODL-ROI-'].update(f'ROI: {hodl_roi:.2f}%')
    window['-HODL-APR-'].update(f'APR: {hodl_apr:.2f}%')
    
    # Detalhes posição
    underlying_usd = float(data.get('underlying_value', 0))
    underlying_brl = underlying_usd * usd_brl
    in_range = "✅ Sim" if data.get('in_range') else "❌ Não"
    age = float(data.get('age', 0))
    
    window['-UNDERLYING-USD-'].update(f'Valor Underlying USD: ${underlying_usd:.2f}')
    window['-UNDERLYING-BRL-'].update(f'Valor Underlying BRL: R$ {underlying_brl:.2f}')
    window['-IN-RANGE-'].update(f'In Range: {in_range}')
    window['-AGE-'].update(f'Age (dias): {age:.2f}')
    
    # Tokens
    tokens = data.get("tokens", {})
    token_layout = []
    for addr, token_info in tokens.items():
        symbol = token_info.get("symbol", "N/A")
        price = float(token_info.get("price", 0))
        token_layout.append([sg.Text(f'{symbol}: ${price:.2f}', font=label_font)])
    
    window['-TOKENS-'].update(sg.Column(token_layout if token_layout else [[sg.Text('Sem tokens')]]))
    
    window['-STATUS-'].update('Status: ✅ Dados carregados com sucesso', text_color='#2ecc71')


def main():
    window = create_window()
    
    # Carregar dados iniciais
    threading.Thread(target=fetch_data_thread, args=(window,), daemon=True).start()
    
    last_update = datetime.now()
    auto_refresh = True
    
    while True:
        timeout = 100 if auto_refresh else None
        event, values = window.read(timeout=timeout)
        
        if event == sg.WINDOW_CLOSED or event == '❌ Sair':
            break
        
        elif event == '-THREAD-':
            if values['-THREAD-']:
                data, usd_brl = values['-THREAD-']
                update_ui(window, data, usd_brl)
                last_update = datetime.now()
            else:
                window['-STATUS-'].update('Status: ❌ Erro ao carregar dados', text_color='#e74c3c')
        
        elif event == '-REFRESH-':
            window['-STATUS-'].update('Status: ⏳ Carregando...', text_color='#f39c12')
            threading.Thread(target=fetch_data_thread, args=(window,), daemon=True).start()
        
        elif event == '-AUTO-REFRESH-':
            auto_refresh = values['-AUTO-REFRESH-']
        
        # Auto-refresh a cada 60 segundos
        if auto_refresh and (datetime.now() - last_update).seconds >= 60:
            threading.Thread(target=fetch_data_thread, args=(window,), daemon=True).start()
    
    window.close()


if __name__ == "__main__":
    main()
