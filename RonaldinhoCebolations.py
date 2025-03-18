import sys
import time
import threading
import random
import win32api
import win32con
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QSpinBox, 
                            QCheckBox, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import keyboard

class RonaldinhoCebolations(QMainWindow):
    def __init__(self):
        super().__init__()
        self.clicking = False
        self.mouse4_pressed = False
        self.total_clicks = 0
        self.last_click_time = time.time()
        self.cps = 0
        self.mouse_listener = None
        self.initUI()
        self.start_mouse_listener()
        
    def initUI(self):
        self.setWindowTitle('RonaldinhoCebolations')
        self.setFixedSize(400, 500)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Contador de cliques
        clicks_group = QGroupBox("Contador de Cliques")
        clicks_layout = QVBoxLayout()
        self.clicks_label = QLabel('0')
        self.clicks_label.setAlignment(Qt.AlignCenter)
        self.clicks_label.setFont(QFont('Arial', 24, QFont.Bold))
        clicks_layout.addWidget(self.clicks_label)
        clicks_group.setLayout(clicks_layout)
        layout.addWidget(clicks_group)
        
        # CPS
        cps_group = QGroupBox("Cliques por Segundo")
        cps_layout = QVBoxLayout()
        self.cps_label = QLabel('0.0 CPS')
        self.cps_label.setAlignment(Qt.AlignCenter)
        self.cps_label.setFont(QFont('Arial', 24, QFont.Bold))
        cps_layout.addWidget(self.cps_label)
        cps_group.setLayout(cps_layout)
        layout.addWidget(cps_group)
        
        # Status
        self.status_label = QLabel('Status: Parado')
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont('Arial', 12, QFont.Bold))
        layout.addWidget(self.status_label)
        
        # Área da imagem nativa
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(150)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a2a;
                border: 2px dashed #4a4a4a;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Botões de controle
        control_group = QGroupBox("Controles")
        control_layout = QVBoxLayout()
        
        # Botão Iniciar/Parar
        self.start_button = QPushButton('Iniciar (F6)')
        self.start_button.clicked.connect(self.toggle_clicking)
        control_layout.addWidget(self.start_button)
        
        # Botão Reset
        self.reset_button = QPushButton('Reset (F7)')
        self.reset_button.clicked.connect(self.reset_clicks)
        control_layout.addWidget(self.reset_button)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Configurações de clique
        click_settings = QGroupBox("Configurações de Clique")
        click_layout = QVBoxLayout()
        
        # Variação de intervalo
        interval_layout = QHBoxLayout()
        interval_label = QLabel('Variação de CPS:')
        interval_layout.addWidget(interval_label)
        
        # CPS mínimo
        min_interval_layout = QVBoxLayout()
        min_interval_label = QLabel('Mínimo')
        min_interval_label.setAlignment(Qt.AlignCenter)
        self.min_interval_spin = QSpinBox()
        self.min_interval_spin.setRange(1, 20)
        self.min_interval_spin.setValue(10)
        self.min_interval_spin.setSingleStep(1)
        self.min_interval_spin.setSuffix(" CPS")
        min_interval_layout.addWidget(min_interval_label)
        min_interval_layout.addWidget(self.min_interval_spin)
        
        # CPS máximo
        max_interval_layout = QVBoxLayout()
        max_interval_label = QLabel('Máximo')
        max_interval_label.setAlignment(Qt.AlignCenter)
        self.max_interval_spin = QSpinBox()
        self.max_interval_spin.setRange(1, 20)
        self.max_interval_spin.setValue(15)
        self.max_interval_spin.setSingleStep(1)
        self.max_interval_spin.setSuffix(" CPS")
        max_interval_layout.addWidget(max_interval_label)
        max_interval_layout.addWidget(self.max_interval_spin)
        
        # Adicionar layouts de intervalo ao layout principal
        interval_layout.addLayout(min_interval_layout)
        interval_layout.addLayout(max_interval_layout)
        click_layout.addLayout(interval_layout)
        
        # Tipo de clique
        click_type_layout = QHBoxLayout()
        click_type_label = QLabel('Tipo de Clique:')
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(['Clique Simples'])
        click_type_layout.addWidget(click_type_label)
        click_type_layout.addWidget(self.click_type_combo)
        click_layout.addLayout(click_type_layout)
        
        click_settings.setLayout(click_layout)
        layout.addWidget(click_settings)
        
        # Atalhos de teclado
        keyboard.on_press_key('F6', lambda _: self.toggle_clicking())
        keyboard.on_press_key('F7', lambda _: self.reset_clicks())
        
        # Conectar sinais para validação
        self.min_interval_spin.valueChanged.connect(self.validate_intervals)
        self.max_interval_spin.valueChanged.connect(self.validate_intervals)
        
        # Carregar imagem nativa
        pixmap = QPixmap("ronaldinho.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("RonaldinhoCebolations")
        
    def start_mouse_listener(self):
        def check_mouse():
            while True:
                if self.clicking:
                    # Verifica se o Mouse4 está pressionado
                    self.mouse4_pressed = win32api.GetAsyncKeyState(0x05) & 0x8000 != 0
                time.sleep(0.01)
        
        self.mouse_listener = threading.Thread(target=check_mouse, daemon=True)
        self.mouse_listener.start()
        
    def toggle_clicking(self):
        if not self.clicking:
            self.start_clicking()
        else:
            self.stop_clicking()
            
    def start_clicking(self):
        self.clicking = True
        self.start_button.setEnabled(False)
        self.status_label.setText('Status: Ativo')
        self.click_thread = threading.Thread(target=self.click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()
        
    def stop_clicking(self):
        self.clicking = False
        self.start_button.setEnabled(True)
        self.status_label.setText('Status: Parado')
        
    def click_loop(self):
        while self.clicking:
            if self.mouse4_pressed:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    
                self.total_clicks += 1
                self.clicks_label.setText(str(self.total_clicks))
                
                # Gerar intervalo aleatório entre mínimo e máximo CPS
                min_cps = self.min_interval_spin.value()
                max_cps = self.max_interval_spin.value()
                random_cps = random.randint(min_cps, max_cps)
                
                # Converter CPS para milissegundos
                interval_ms = 1000 / random_cps
                time.sleep(interval_ms / 1000)
        
    def validate_intervals(self):
        min_val = self.min_interval_spin.value()
        max_val = self.max_interval_spin.value()
        
        if min_val > max_val:
            if self.min_interval_spin == self.sender():
                self.max_interval_spin.setValue(min_val)
            else:
                self.min_interval_spin.setValue(max_val)
        
    def reset_clicks(self):
        self.total_clicks = 0
        self.clicks_label.setText('0')
        self.cps = 0
        self.cps_label.setText('0.0 CPS')
        
    def closeEvent(self, event):
        self.clicking = False
        if hasattr(self, 'click_thread') and self.click_thread:
            self.click_thread.join(timeout=0.1)
        if self.mouse_listener:
            self.mouse_listener.join(timeout=0.1)
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clicker = RonaldinhoCebolations()
    clicker.show()
    sys.exit(app.exec_()) 