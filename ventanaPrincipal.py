import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

alto = 300
ancho = 400

class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, tamano, agente):
        super().__init__()
        uic.loadUi('prueba.ui', self)
        self.entornoWidget.configurar(tamano, agente)
        self.repaint()
