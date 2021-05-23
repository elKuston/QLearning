from PyQt5 import QtGui, QtCore, QtWidgets, uic
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


import sys
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class VentanaMetricas(QtWidgets.QMainWindow):

    class Canvas(FigureCanvasQTAgg):
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            super(VentanaMetricas.Canvas, self).__init__(fig)

    def __init__(self, lista_algoritmos):
        super().__init__()
        self.lista_algoritmos = lista_algoritmos
        self.lienzo = VentanaMetricas.Canvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.lienzo, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.lienzo)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.show()
        self.__referencias_plt = dict([])
        self.plot_data_x = dict([])
        self.plot_data_y = dict([])

        for alg in lista_algoritmos:
            self.plot_data_x[alg] = []
            self.plot_data_y[alg] = []


    def add_plot_data(self, x, y, alg_name):
        if alg_name not in self.plot_data_x:
            self.plot_data_x[alg_name] = []
        self.plot_data_x[alg_name].append(x)
        if alg_name not in self.plot_data_y:
            self.plot_data_y[alg_name] = []
        self.plot_data_y[alg_name].append(y)

        #if alg_name not in self.__referencias_plt:
        self.lienzo.axes.cla()
        for alg in self.lista_algoritmos:
            refs = self.lienzo.axes.plot(self.plot_data_x[alg], self.plot_data_y[alg], label=alg)
            #self.__referencias_plt[alg_name] = refs[0]
        #else:
        #    self.__referencias_plt[alg_name].set_xdata(self.plot_data_x[alg_name])
        #    self.__referencias_plt[alg_name].set_ydata(self.plot_data_y[alg_name])

        self.lienzo.axes.legend(loc='upper left')
        self.lienzo.draw()
