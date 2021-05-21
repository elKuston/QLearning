from PyQt5 import QtWidgets, uic
from entornoWidget import EntornoWidget
import pyqtgraph as pg

alto = 300
ancho = 400


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, tamano, agente, pantalla):
        super().__init__()
        self.pantalla = pantalla
        uic.loadUi('prueba.ui', self)
        self.entorno.configurar(tamano, agente, pantalla)
        self.repaint()

    def cambiar_entorno(self, tamano, agente):
        nuevo_entorno = EntornoWidget(self.pantalla, tamano, agente)
        padre = self.entorno.parent().layout()
        padre.replaceWidget(self.entorno, nuevo_entorno)
        self.entorno.deleteLater()
        self.entorno = nuevo_entorno
        self.repaint()


class VentanaMetricas(QtWidgets.QMainWindow):
    def __init__(self, lista_nombres_algoritmos):
        super().__init__()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        #uic.loadUi('ventana_metricas.ui', self)
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)
        self.plot_widget.setTitle("Métricas")
        self.plot_widget.addLegend()

        self.plot_data_x = {"none": []}
        self.plot_data_y = {"none": []}
        for alg in lista_nombres_algoritmos:
            self.plot_data_x[alg] = []
            self.plot_data_y[alg] = []
        # for i in range(n_plots):
        #     self.plot_data.append([[], []])  # Para cada plot vamos a tener el objeto para plotear y una lista con todas sus x e y


    def add_plot_data(self, x, y, alg_name, clear):
        self.plot_data_x[alg_name].append(x)
        self.plot_data_y[alg_name].append(y)
        self.plot_widget.plot(self.plot_data_x[alg_name], self.plot_data_y[alg_name], name=alg_name, clear=clear)
        self.repaint()
