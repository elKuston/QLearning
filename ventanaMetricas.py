from PyQt5 import QtWidgets, uic

alto = 300
ancho = 400


class VentanaMetricas(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ventana_metricas.ui', self)
        self.repaint()
