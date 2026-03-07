#!/usr/bin/env python3
"""
Aplicação Desktop com Tkinter
Display elegante para Fees e Impermanent Loss
Compatível com Python 3.12+
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


class FeeCalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fee Calc Dashboard")
        self.root.geometry("1000x900")
        self.root.configure(bg="#1a1a1a")
        
        # Estilos
        self.setup_styles()
        
        # Build UI
        self.create_widgets()
        
        # Auto-refresh control
        self.auto_refresh = True
        self.last_update = datetime.now()
        
        # Initial data fetch
        self.refresh_data()
        
        # Schedule auto-refresh
        self.schedule_refresh()
    
    def setup_styles(self):
        """Configura os estilos da aplicação."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores
        bg_dark = "#1a1a1a"
        bg_card = "#2c3e50"
        fg_light = "#ecf0f1"
        accent = "#3498db"
        
        style.configure("TLabel", background=bg_dark, foreground=fg_light)
        style.configure("Title.TLabel", font=("Arial", 20, "bold"), foreground="#2ecc71")
        style.configure("Header.TLabel", font=("Arial", 12, "bold"), foreground="#3498db")
        style.configure("Value.TLabel", font=("Arial", 16, "bold"))
        style.configure("Card.TFrame", background=bg_card, relief="sunken", borderwidth=2)
        style.configure("TButton", font=("Arial", 10))
    
    def create_widgets(self):
        """Cria todos os widgets da interface."""
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ===== HEADER =====
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="💰 FEE CALC DASHBOARD", style="Title.TLabel")
        title_label.pack(side="left")
        
        subtitle_label = ttk.Label(main_frame, text="Monitorando Posição Uniswap V3 no Arbitrum", foreground="#95a5a6")
        subtitle_label.pack(fill="x", pady=(0, 10))
        
        # Info bar
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=(0, 10))
        
        self.position_label = ttk.Label(info_frame, text=f"Posição ID: {POSITION_ID}")
        self.position_label.pack(side="left", padx=10)
        
        self.exchange_label = ttk.Label(info_frame, text="Taxa USD/BRL: -")
        self.exchange_label.pack(side="left", padx=10)
        
        self.time_label = ttk.Label(info_frame, text="")
        self.time_label.pack(side="right", padx=10)
        
        separator1 = ttk.Separator(main_frame, orient="horizontal")
        separator1.pack(fill="x", pady=10)
        
        # ===== CARDS PRINCIPAIS =====
        cards_frame = ttk.Frame(main_frame)
        cards_frame.pack(fill="x", pady=10)
        
        # Fees Card
        self.card_fees_frame = ttk.Frame(cards_frame, style="Card.TFrame")
        self.card_fees_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(self.card_fees_frame, text="💵 FEES COLETADAS", style="Header.TLabel").pack(padx=10, pady=(10, 5))
        self.fees_usd = ttk.Label(self.card_fees_frame, text="$0.00", style="Value.TLabel", foreground="#2ecc71")
        self.fees_usd.pack(padx=10)
        self.fees_brl = ttk.Label(self.card_fees_frame, text="R$ 0.00", foreground="#27ae60")
        self.fees_brl.pack(padx=10, pady=(0, 10))
        
        # IL Card
        self.card_il_frame = ttk.Frame(cards_frame, style="Card.TFrame")
        self.card_il_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(self.card_il_frame, text="⚠️  IMPERMANENT LOSS", style="Header.TLabel").pack(padx=10, pady=(10, 5))
        self.il_usd = ttk.Label(self.card_il_frame, text="$0.00", style="Value.TLabel", foreground="#e74c3c")
        self.il_usd.pack(padx=10)
        self.il_brl = ttk.Label(self.card_il_frame, text="R$ 0.00", foreground="#c0392b")
        self.il_brl.pack(padx=10, pady=(0, 10))
        
        # PnL Card
        self.card_pnl_frame = ttk.Frame(cards_frame, style="Card.TFrame")
        self.card_pnl_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(self.card_pnl_frame, text="📊 TOTAL PnL", style="Header.TLabel").pack(padx=10, pady=(10, 5))
        self.pnl_usd = ttk.Label(self.card_pnl_frame, text="$0.00", style="Value.TLabel", foreground="#3498db")
        self.pnl_usd.pack(padx=10)
        self.pnl_brl = ttk.Label(self.card_pnl_frame, text="R$ 0.00", foreground="#2980b9")
        self.pnl_brl.pack(padx=10, pady=(0, 10))
        
        separator2 = ttk.Separator(main_frame, orient="horizontal")
        separator2.pack(fill="x", pady=10)
        
        # ===== DETALHES =====
        details_frame = ttk.Frame(main_frame)
        details_frame.pack(fill="both", expand=True, pady=10)
        
        # Coluna 1 - HODL
        hodl_frame = ttk.Frame(details_frame, style="Card.TFrame")
        hodl_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(hodl_frame, text="📈 SE TIVESSE FEITO HODL", style="Header.TLabel", foreground="#f39c12").pack(padx=10, pady=(10, 5), anchor="w")
        self.hodl_pnl_usd = ttk.Label(hodl_frame, text="PnL USD: $0.00", font=("Arial", 10))
        self.hodl_pnl_usd.pack(padx=10, anchor="w")
        self.hodl_pnl_brl = ttk.Label(hodl_frame, text="PnL BRL: R$ 0.00", font=("Arial", 10))
        self.hodl_pnl_brl.pack(padx=10, anchor="w")
        self.hodl_roi = ttk.Label(hodl_frame, text="ROI: 0.00%", font=("Arial", 10))
        self.hodl_roi.pack(padx=10, anchor="w")
        self.hodl_apr = ttk.Label(hodl_frame, text="APR: 0.00%", font=("Arial", 10))
        self.hodl_apr.pack(padx=10, anchor="w", pady=(0, 10))
        
        # Coluna 2 - POSIÇÃO
        pos_frame = ttk.Frame(details_frame, style="Card.TFrame")
        pos_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(pos_frame, text="📍 DETALHES DA POSIÇÃO", style="Header.TLabel", foreground="#9b59b6").pack(padx=10, pady=(10, 5), anchor="w")
        self.underlying_usd = ttk.Label(pos_frame, text="Valor Underlying USD: $0.00", font=("Arial", 10))
        self.underlying_usd.pack(padx=10, anchor="w")
        self.underlying_brl = ttk.Label(pos_frame, text="Valor Underlying BRL: R$ 0.00", font=("Arial", 10))
        self.underlying_brl.pack(padx=10, anchor="w")
        self.in_range = ttk.Label(pos_frame, text="In Range: -", font=("Arial", 10))
        self.in_range.pack(padx=10, anchor="w")
        self.age = ttk.Label(pos_frame, text="Age (dias): 0.00", font=("Arial", 10))
        self.age.pack(padx=10, anchor="w", pady=(0, 10))
        
        # Coluna 3 - TOKENS
        tokens_frame = ttk.Frame(details_frame, style="Card.TFrame")
        tokens_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        ttk.Label(tokens_frame, text="🪙 TOKENS NA POSIÇÃO", style="Header.TLabel", foreground="#1abc9c").pack(padx=10, pady=(10, 5), anchor="w")
        self.tokens_container = ttk.Frame(tokens_frame)
        self.tokens_container.pack(padx=10, anchor="w", fill="both", expand=True)
        
        separator3 = ttk.Separator(main_frame, orient="horizontal")
        separator3.pack(fill="x", pady=10)
        
        # ===== CONTROLES =====
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=10)
        
        self.refresh_btn = ttk.Button(controls_frame, text="🔄 Atualizar", command=self.on_refresh_click)
        self.refresh_btn.pack(side="left", padx=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        auto_refresh_check = ttk.Checkbutton(controls_frame, text="Auto-refresh (60s)", variable=self.auto_refresh_var)
        auto_refresh_check.pack(side="left", padx=5)
        
        exit_btn = ttk.Button(controls_frame, text="❌ Sair", command=self.root.quit)
        exit_btn.pack(side="right", padx=5)
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Status: ⏳ Carregando dados iniciais...", foreground="#f39c12")
        self.status_label.pack(fill="x", pady=(10, 0))
        
        # Update time display
        self.update_time()
    
    def update_time(self):
        """Atualiza a hora exibida."""
        self.time_label.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.update_time)
    
    def on_refresh_click(self):
        """Handler para clique no botão atualizar."""
        self.refresh_data()
    
    def refresh_data(self):
        """Busca dados em thread."""
        self.refresh_btn.config(state="disabled")
        self.status_label.config(text="Status: ⏳ Carregando...", foreground="#f39c12")
        
        def fetch():
            try:
                data = get_performance_metrics()
                usd_brl = get_exchange_rate()
                
                if data and usd_brl:
                    self.root.after(0, self.update_ui, data, usd_brl)
                else:
                    self.root.after(0, self.show_error, "Erro ao carregar dados")
            except Exception as e:
                self.root.after(0, self.show_error, str(e))
        
        thread = threading.Thread(target=fetch, daemon=True)
        thread.start()
    
    def show_error(self, error_msg):
        """Exibe mensagem de erro."""
        self.status_label.config(text=f"Status: ❌ {error_msg}", foreground="#e74c3c")
        self.refresh_btn.config(state="normal")
    
    def update_ui(self, data, usd_brl):
        """Atualiza toda a interface com os novos dados."""
        
        performance = data.get("performance", {})
        hodl = performance.get("hodl", {})
        
        # Calcular valores
        fees_value_usd = float(data.get('fees_value', 0))
        fees_value_brl = fees_value_usd * usd_brl
        
        il_usd = float(hodl.get('il', 0))
        il_brl = il_usd * usd_brl
        
        total_pnl_usd = fees_value_usd + il_usd
        total_pnl_brl = total_pnl_usd * usd_brl
        
        # Atualizar header
        self.exchange_label.config(text=f"Taxa USD/BRL: R$ {usd_brl:.2f}")
        
        # Atualizar cards
        self.fees_usd.config(text=f"${fees_value_usd:.2f}")
        self.fees_brl.config(text=f"R$ {fees_value_brl:.2f}")
        
        color_il = "#e74c3c" if il_usd < 0 else "#2ecc71"
        self.il_usd.config(text=f"${il_usd:.2f}", foreground=color_il)
        self.il_brl.config(text=f"R$ {il_brl:.2f}")
        
        color_pnl = "#2ecc71" if total_pnl_usd >= 0 else "#e74c3c"
        self.pnl_usd.config(text=f"${total_pnl_usd:.2f}", foreground=color_pnl)
        self.pnl_brl.config(text=f"R$ {total_pnl_brl:.2f}")
        
        # Detalhes HODL
        hodl_pnl_usd = float(hodl.get('pnl', 0))
        hodl_pnl_brl = hodl_pnl_usd * usd_brl
        hodl_roi = float(hodl.get('roi', 0)) * 100
        hodl_apr = float(hodl.get('apr', 0))
        
        self.hodl_pnl_usd.config(text=f"PnL USD: ${hodl_pnl_usd:.2f}")
        self.hodl_pnl_brl.config(text=f"PnL BRL: R$ {hodl_pnl_brl:.2f}")
        self.hodl_roi.config(text=f"ROI: {hodl_roi:.2f}%")
        self.hodl_apr.config(text=f"APR: {hodl_apr:.2f}%")
        
        # Detalhes posição
        underlying_usd = float(data.get('underlying_value', 0))
        underlying_brl = underlying_usd * usd_brl
        in_range = "✅ Sim" if data.get('in_range') else "❌ Não"
        age = float(data.get('age', 0))
        
        self.underlying_usd.config(text=f"Valor Underlying USD: ${underlying_usd:.2f}")
        self.underlying_brl.config(text=f"Valor Underlying BRL: R$ {underlying_brl:.2f}")
        self.in_range.config(text=f"In Range: {in_range}")
        self.age.config(text=f"Age (dias): {age:.2f}")
        
        # Tokens
        self.update_tokens(data.get("tokens", {}))
        
        # Status
        self.status_label.config(text="Status: ✅ Dados carregados com sucesso", foreground="#2ecc71")
        self.refresh_btn.config(state="normal")
        self.last_update = datetime.now()
    
    def update_tokens(self, tokens):
        """Atualiza a exibição de tokens."""
        for widget in self.tokens_container.winfo_children():
            widget.destroy()
        
        if tokens:
            for addr, token_info in tokens.items():
                symbol = token_info.get("symbol", "N/A")
                price = float(token_info.get("price", 0))
                
                token_label = ttk.Label(
                    self.tokens_container,
                    text=f"{symbol}: ${price:.2f}",
                    foreground="#1abc9c",
                    font=("Arial", 10)
                )
                token_label.pack(anchor="w")
        else:
            empty_label = ttk.Label(self.tokens_container, text="Sem tokens")
            empty_label.pack(anchor="w")
    
    def schedule_refresh(self):
        """Agenda auto-refresh a cada 60 segundos."""
        if self.auto_refresh_var.get() and (datetime.now() - self.last_update).seconds >= 60:
            self.refresh_data()
        
        self.root.after(5000, self.schedule_refresh)


def main():
    root = tk.Tk()
    app = FeeCalcApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
