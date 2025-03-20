import sys
import time
import random
import win32api
import win32con
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QSpinBox, QGroupBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AutoClicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RonaldinhoCebolations")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
            QSpinBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #3d3d3d;
                border: none;
                border-radius: 2px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #4d4d4d;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                margin-top: 12px;
                padding-top: 16px;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }
        """)
        
        # Variáveis de controle
        self.clicking = False
        self.last_click_time = 0
        self.mouse4_pressed = False
        self.next_click_time = 0
        self.last_cps = 0  # Para evitar repetição do mesmo valor
        self.clicks_count = 0  # Para debug
        self.last_debug_time = 0  # Para debug
        
        # Configuração da interface
        self.setup_ui()
        
        # Timer para verificar teclas e mouse
        self.key_timer = QTimer()
        self.key_timer.timeout.connect(self.check_keys)
        self.key_timer.start(10)  # Verifica a cada 10ms
        
        # Timer para cliques
        self.click_timer = QTimer()
        self.click_timer.timeout.connect(self.click_loop)
        self.click_timer.start(1)  # Verifica a cada 1ms para maior precisão
        
        # Carregar ícone
        try:
            icon_path = resource_path('icone.ico')
            self.setWindowIcon(QIcon(icon_path))
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")
            pass

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Configurações de CPS
        interval_group = QGroupBox("Variação de CPS")
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Mínimo:"))
        self.min_interval = QSpinBox()
        self.min_interval.setRange(1, 20)
        self.min_interval.setValue(10)
        self.min_interval.setSuffix(" CPS")
        self.min_interval.setMinimumWidth(100)
        interval_layout.addWidget(self.min_interval)
        
        interval_layout.addWidget(QLabel("Máximo:"))
        self.max_interval = QSpinBox()
        self.max_interval.setRange(1, 20)
        self.max_interval.setValue(15)
        self.max_interval.setSuffix(" CPS")
        self.max_interval.setMinimumWidth(100)
        interval_layout.addWidget(self.max_interval)
        
        interval_group.setLayout(interval_layout)
        layout.addWidget(interval_group)

        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Status: Parado")
        self.status_label.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Debug
        debug_group = QGroupBox("Debug")
        debug_layout = QVBoxLayout()
        self.debug_label = QLabel("CPS Atual: 0")
        self.debug_label.setAlignment(Qt.AlignCenter)
        debug_layout.addWidget(self.debug_label)
        debug_group.setLayout(debug_layout)
        layout.addWidget(debug_group)

        # Área da imagem
        image_group = QGroupBox("RonaldinhoCebolations")
        image_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        try:
            pixmap = QPixmap(resource_path('ronaldinho.png'))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
            else:
                self.image_label.setText("RonaldinhoCebolations")
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            self.image_label.setText("RonaldinhoCebolations")
        image_layout.addWidget(self.image_label)
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)

    def check_keys(self):
        # Verifica Mouse4
        self.mouse4_pressed = win32api.GetAsyncKeyState(win32con.VK_XBUTTON1) & 0x8000 != 0
        if self.mouse4_pressed and not self.clicking:
            self.toggle_clicking()
        elif not self.mouse4_pressed and self.clicking:
            self.toggle_clicking()

    def get_random_cps(self):
        min_cps = self.min_interval.value()
        max_cps = self.max_interval.value()
        
        # Se min e max são iguais, retorna o valor
        if min_cps == max_cps:
            return min_cps
            
        # Gera um valor aleatório diferente do último usado
        while True:
            cps = random.randint(min_cps, max_cps)
            if cps != self.last_cps:
                self.last_cps = cps
                return cps

    def click_loop(self):
        if not self.clicking or not self.mouse4_pressed:
            return
            
        current_time = time.time()
        
        # Se já passou o tempo do próximo clique
        if current_time >= self.next_click_time:
            # Gera um valor aleatório inteiro entre min e max
            cps = self.get_random_cps()
            
            # Atualiza o debug
            self.debug_label.setText(f"CPS Atual: {cps}")
            
            # Calcula o próximo tempo de clique
            interval = 1000 / cps  # Converte CPS para milissegundos
            self.next_click_time = current_time + (interval / 1000)  # Converte para segundos
            
            # Adiciona uma pequena variação aleatória no tempo do clique
            click_duration = random.uniform(0.008, 0.015)
            
            # Executa o clique
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(click_duration)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            
            # Debug de contagem de cliques por segundo
            self.clicks_count += 1
            if current_time - self.last_debug_time >= 1.0:
                actual_cps = self.clicks_count
                print(f"CPS Real: {actual_cps}")
                self.clicks_count = 0
                self.last_debug_time = current_time

    def toggle_clicking(self):
        self.clicking = not self.clicking
        if self.clicking:
            self.status_label.setText("Status: Rodando")
            self.next_click_time = time.time()  # Inicializa o próximo clique
            self.last_cps = 0  # Reseta o último CPS usado
            self.clicks_count = 0  # Reseta o contador de cliques
            self.last_debug_time = time.time()  # Reseta o tempo do último debug
        else:
            self.status_label.setText("Status: Parado")

    def closeEvent(self, event):
        self.clicking = False
        self.click_timer.stop()
        self.key_timer.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Configurar ícone no nível da aplicação
    try:
        app_icon = QIcon(resource_path('icone.ico'))
        app.setWindowIcon(app_icon)
    except Exception as e:
        print(f"Erro ao carregar ícone da aplicação: {e}")
    
    window = AutoClicker()
    window.show()
    sys.exit(app.exec_()) 