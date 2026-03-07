#!/usr/bin/env python3
"""
Aplicação Desktop com PyQt6
Interface moderna e profissional para Fees e Impermanent Loss
"""

import sys
import requests
import threading
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QCheckBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap

POSITION_ID = 5303576


class DataFetcher(QObject):
    """Worker thread para buscar dados sem congelar UI."""
    data_ready = pyqtSignal(dict, float)
    error_occurred = pyqtSignal(str)
    
    def fetch_data(self):
        """Busca dados de performance e taxa de câmbio."""
        try:
            # Buscar performance metrics
            url = f"https://api.revert.finance/v1/positions/arbitrum/uniswapv3/{POSITION_ID}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200 and response.json().get("success"):
                data = response.json().get("data", {})
            else:
                self.error_occurred.emit("Erro: API retornou status inválido")
                return
            
            # Buscar taxa de câmbio
            exchange_response = requests.get(
                "https://economia.awesomeapi.com.br/json/last/USD-BRL"
            )
            
            if exchange_response.status_code == 200:
                usd_brl = float(exchange_response.json()["USDBRL"]["bid"])
            else:
                self.error_occurred.emit("Erro: Não foi possível obter câmbio")
                return
            
            self.data_ready.emit(data, usd_brl)
        
        except Exception as e:
            self.error_occurred.emit(f"Erro: {str(e)}")


class MetricCard(QFrame):
    """Card para exibir uma métrica."""
    
    def __init__(self, title, icon, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel(f"{icon} {title}")
        title_font = QFont("Arial", 12, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ecf0f1;")
        layout.addWidget(title_label)
        
        # Valor USD
        self.value_usd = QLabel("$0.00")
        usd_font = QFont("Arial", 24, QFont.Weight.Bold)
        self.value_usd.setFont(usd_font)
        self.value_usd.setStyleSheet("color: #3498db;")
        layout.addWidget(self.value_usd)
        
        # Valor BRL
        self.value_brl = QLabel("R$ 0.00")
        brl_font = QFont("Arial", 14)
        self.value_brl.setFont(brl_font)
        self.value_brl.setStyleSheet("color: #95a5a6;")
        layout.addWidget(self.value_brl)
        
        layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(layout)
    
    def update_values(self, usd_value, brl_value, color="#3498db"):
        """Atualiza valores da métrica."""
        self.value_usd.setText(f"${usd_value:.2f}")
        self.value_brl.setText(f"R$ {brl_value:.2f}")
        self.value_usd.setStyleSheet(f"color: {color};")


class FeeCalcApp(QMainWindow):
    """Aplicação principal."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fee Calc Dashboard - Desktop")
        self.setGeometry(100, 100, 1200, 900)
        
        # CSS Global
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a252f;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QCheckBox {
                color: #ecf0f1;
                spacing: 5px;
            }
        """)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ===== HEADER =====
        header_layout = QHBoxLayout()
        
        title = QLabel("💰 FEE CALC DASHBOARD")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2ecc71;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #95a5a6; font-size: 10px;")
        header_layout.addWidget(self.info_label)
        
        main_layout.addLayout(header_layout)
        
        # Subtítulo
        subtitle = QLabel("Monitorando Posição Uniswap V3 no Arbitrum")
        subtitle.setStyleSheet("color: #95a5a6; font-size: 11px;")
        main_layout.addWidget(subtitle)
        
        # Separador
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.Shape.HLine)
        separator1.setStyleSheet("background-color: #34495e;")
        main_layout.addWidget(separator1)
        
        # ===== INFO BAR =====
        info_layout = QHBoxLayout()
        
        self.position_label = QLabel(f"Posição ID: {POSITION_ID}")
        self.position_label.setStyleSheet("color: #ecf0f1;")
        info_layout.addWidget(self.position_label)
        
        self.exchange_label = QLabel("Taxa USD/BRL: -")
        self.exchange_label.setStyleSheet("color: #ecf0f1;")
        info_layout.addWidget(self.exchange_label)
        
        info_layout.addStretch()
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #95a5a6;")
        info_layout.addWidget(self.time_label)
        
        main_layout.addLayout(info_layout)
        
        # Separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setStyleSheet("background-color: #34495e;")
        main_layout.addWidget(separator2)
        
        # ===== CARDS PRINCIPAIS =====
        cards_layout = QHBoxLayout()
        
        self.card_fees = MetricCard("FEES COLETADAS", "💵")
        self.card_il = MetricCard("IMPERMANENT LOSS", "⚠️ ")
        self.card_pnl = MetricCard("TOTAL PnL", "📊")
        
        cards_layout.addWidget(self.card_fees)
        cards_layout.addWidget(self.card_il)
        cards_layout.addWidget(self.card_pnl)
        
        main_layout.addLayout(cards_layout)
        
        # Separador
        separator3 = QFrame()
        separator3.setFrameShape(QFrame.Shape.HLine)
        separator3.setStyleSheet("background-color: #34495e;")
        main_layout.addWidget(separator3)
        
        # ===== DETALHES =====
        details_layout = QHBoxLayout()
        
        # Coluna 1 - HODL
        hodl_frame = QFrame()
        hodl_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                padding: 15px;
            }
        """)
        hodl_layout = QVBoxLayout()
        
        hodl_title = QLabel("📈 SE TIVESSE FEITO HODL")
        hodl_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        hodl_title.setStyleSheet("color: #f39c12;")
        hodl_layout.addWidget(hodl_title)
        
        self.hodl_pnl_usd = QLabel("PnL USD: $0.00")
        self.hodl_pnl_brl = QLabel("PnL BRL: R$ 0.00")
        self.hodl_roi = QLabel("ROI: 0.00%")
        self.hodl_apr = QLabel("APR: 0.00%")
        
        for label in [self.hodl_pnl_usd, self.hodl_pnl_brl, self.hodl_roi, self.hodl_apr]:
            label.setStyleSheet("color: #ecf0f1; font-size: 11px;")
            hodl_layout.addWidget(label)
        
        hodl_layout.addStretch()
        hodl_frame.setLayout(hodl_layout)
        details_layout.addWidget(hodl_frame)
        
        # Coluna 2 - POSIÇÃO
        pos_frame = QFrame()
        pos_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                padding: 15px;
            }
        """)
        pos_layout = QVBoxLayout()
        
        pos_title = QLabel("📍 DETALHES DA POSIÇÃO")
        pos_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        pos_title.setStyleSheet("color: #9b59b6;")
        pos_layout.addWidget(pos_title)
        
        self.underlying_usd = QLabel("Valor Underlying USD: $0.00")
        self.underlying_brl = QLabel("Valor Underlying BRL: R$ 0.00")
        self.in_range = QLabel("In Range: -")
        self.age = QLabel("Age (dias): 0.00")
        
        for label in [self.underlying_usd, self.underlying_brl, self.in_range, self.age]:
            label.setStyleSheet("color: #ecf0f1; font-size: 11px;")
            pos_layout.addWidget(label)
        
        pos_layout.addStretch()
        pos_frame.setLayout(pos_layout)
        details_layout.addWidget(pos_frame)
        
        # Coluna 3 - TOKENS
        tokens_frame = QFrame()
        tokens_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                padding: 15px;
            }
        """)
        tokens_layout = QVBoxLayout()
        
        tokens_title = QLabel("🪙 TOKENS NA POSIÇÃO")
        tokens_title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        tokens_title.setStyleSheet("color: #1abc9c;")
        tokens_layout.addWidget(tokens_title)
        
        self.tokens_container = QVBoxLayout()
        self.tokens_container.addWidget(QLabel("Carregando..."))
        tokens_layout.addLayout(self.tokens_container)
        
        tokens_layout.addStretch()
        tokens_frame.setLayout(tokens_layout)
        details_layout.addWidget(tokens_frame)
        
        main_layout.addLayout(details_layout)
        
        # Separador
        separator4 = QFrame()
        separator4.setFrameShape(QFrame.Shape.HLine)
        separator4.setStyleSheet("background-color: #34495e;")
        main_layout.addWidget(separator4)
        
        # ===== CONTROLES =====
        controls_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Atualizar")
        self.refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(self.refresh_btn)
        
        self.auto_refresh_check = QCheckBox("Auto-refresh (60s)")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.setStyleSheet("color: #ecf0f1;")
        controls_layout.addWidget(self.auto_refresh_check)
        
        controls_layout.addStretch()
        
        exit_btn = QPushButton("❌ Sair")
        exit_btn.clicked.connect(self.close)
        controls_layout.addWidget(exit_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Status
        self.status_label = QLabel("Status: ⏳ Carregando dados iniciais...")
        self.status_label.setStyleSheet("color: #f39c12; font-size: 10px;")
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        central_widget.setLayout(main_layout)
        
        # ===== TIMER PARA AUTO-REFRESH =====
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(60000)  # 60 segundos
        
        # ===== WORKER THREAD =====
        self.data_fetcher = DataFetcher()
        self.data_fetcher.data_ready.connect(self.on_data_ready)
        self.data_fetcher.error_occurred.connect(self.on_error)
        
        # Carrega dados inicialmente
        self.refresh_data()
        
        # Update time
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
    
    def refresh_data(self):
        """Inicia busca de dados em thread."""
        if not self.auto_refresh_check.isChecked() and self.timer.isActive():
            return
        
        self.status_label.setText("Status: ⏳ Carregando...")
        self.status_label.setStyleSheet("color: #f39c12;")
        self.refresh_btn.setEnabled(False)
        
        # Executar fetch em thread
        thread = threading.Thread(target=self.data_fetcher.fetch_data, daemon=True)
        thread.start()
    
    def on_data_ready(self, data, usd_brl):
        """Callback quando dados estão prontos."""
        self.update_ui(data, usd_brl)
        self.refresh_btn.setEnabled(True)
        self.status_label.setText("Status: ✅ Dados carregados")
        self.status_label.setStyleSheet("color: #2ecc71;")
    
    def on_error(self, error_msg):
        """Callback quando há erro."""
        self.status_label.setText(f"Status: ❌ {error_msg}")
        self.status_label.setStyleSheet("color: #e74c3c;")
        self.refresh_btn.setEnabled(True)
    
    def update_time(self):
        """Atualiza hora atual."""
        self.time_label.setText(datetime.now().strftime("%H:%M:%S"))
    
    def update_ui(self, data, usd_brl):
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
        
        # Atualizar câmbio
        self.exchange_label.setText(f"Taxa USD/BRL: R$ {usd_brl:.2f}")
        
        # Atualizar cards
        self.card_fees.update_values(fees_value_usd, fees_value_brl, "#2ecc71")
        
        color_il = "#e74c3c" if il_usd < 0 else "#2ecc71"
        self.card_il.update_values(il_usd, il_brl, color_il)
        
        color_pnl = "#2ecc71" if total_pnl_usd >= 0 else "#e74c3c"
        self.card_pnl.update_values(total_pnl_usd, total_pnl_brl, color_pnl)
        
        # Detalhes HODL
        hodl_pnl_usd = float(hodl.get('pnl', 0))
        hodl_pnl_brl = hodl_pnl_usd * usd_brl
        hodl_roi = float(hodl.get('roi', 0)) * 100
        hodl_apr = float(hodl.get('apr', 0))
        
        self.hodl_pnl_usd.setText(f"PnL USD: ${hodl_pnl_usd:.2f}")
        self.hodl_pnl_brl.setText(f"PnL BRL: R$ {hodl_pnl_brl:.2f}")
        self.hodl_roi.setText(f"ROI: {hodl_roi:.2f}%")
        self.hodl_apr.setText(f"APR: {hodl_apr:.2f}%")
        
        # Detalhes posição
        underlying_usd = float(data.get('underlying_value', 0))
        underlying_brl = underlying_usd * usd_brl
        in_range = "✅ Sim" if data.get('in_range') else "❌ Não"
        age = float(data.get('age', 0))
        
        self.underlying_usd.setText(f"Valor Underlying USD: ${underlying_usd:.2f}")
        self.underlying_brl.setText(f"Valor Underlying BRL: R$ {underlying_brl:.2f}")
        self.in_range.setText(f"In Range: {in_range}")
        self.age.setText(f"Age (dias): {age:.2f}")
        
        # Tokens
        self.update_tokens(data.get("tokens", {}))
    
    def update_tokens(self, tokens):
        """Atualiza exibição de tokens."""
        # Limpar widgets anteriores
        while self.tokens_container.count():
            self.tokens_container.takeAt(0).widget().deleteLater()
        
        if tokens:
            for addr, token_info in tokens.items():
                symbol = token_info.get("symbol", "N/A")
                price = float(token_info.get("price", 0))
                
                token_label = QLabel(f"{symbol}: ${price:.2f}")
                token_label.setStyleSheet("color: #1abc9c; font-size: 11px;")
                self.tokens_container.addWidget(token_label)
        else:
            empty_label = QLabel("Sem tokens")
            empty_label.setStyleSheet("color: #95a5a6;")
            self.tokens_container.addWidget(empty_label)


def main():
    app = QApplication(sys.argv)
    window = FeeCalcApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
