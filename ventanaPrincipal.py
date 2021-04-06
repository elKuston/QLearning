import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from entornoWidget import EntornoWidget

alto = 300
ancho = 400


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, tamano, agente):
        super().__init__()
        uic.loadUi('prueba.ui', self)
        self.entorno.configurar(tamano, agente)
        self.repaint()

    def cambiar_entorno(self, tamano, agente):
        nuevo_entorno = EntornoWidget(tamano, agente)
        padre = self.entorno.parent().layout()
        padre.replaceWidget(self.entorno, nuevo_entorno)
        self.entorno.deleteLater()
        self.entorno = nuevo_entorno
        self.repaint()

