import random

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.Qt import Qt
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis, QValueAxis

import utils
from entornoWidget import EntornoWidget
from politica import EpsilonGreedy
from threadsSegundoPlano import ThreadBenchmark

alto = 300
ancho = 400


class VentanaPrincipal(QtWidgets.QMainWindow):
    def __init__(self, tamano, agente, pantalla):
        super().__init__()
        self.pantalla = pantalla
        uic.loadUi('prueba.ui', self)
        self.setWindowIcon(QtGui.QIcon('icon-crop.png'))
        self.entorno.configurar(tamano, agente, pantalla)
        self.repaint()

    def cambiar_entorno(self, tamano, agente):
        nuevo_entorno = EntornoWidget(self.pantalla, tamano, agente)
        padre = self.entorno.parent().layout()
        padre.replaceWidget(self.entorno, nuevo_entorno)
        self.entorno.deleteLater()
        self.entorno = nuevo_entorno
        self.repaint()


class VentanaMetricasPyqtgraph(QtWidgets.QMainWindow):
    def __init__(self, lista_algoritmos):
        super().__init__()

        #uic.loadUi('ventana_metricas.ui', self)
        #self.graphWidget = self.pyqtGraph
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.__referencias_plt = dict([])
        self.__colores = dict([])
        self.plot_data_x = dict([])
        self.plot_data_y = dict([])
        colores = utils.generar_n_colores(len(lista_algoritmos))
        for i in range(len(lista_algoritmos)):
            self.__colores[lista_algoritmos[i]] = tuple(np.array(colores[i])*255)

        for alg in lista_algoritmos:
            self.__referencias_plt[alg] = None
            self.plot_data_x[alg] = []
            self.plot_data_y[alg] = []

        self.graphWidget.setBackground('w')
        # Add Title
        self.graphWidget.setTitle("Eficacia del entrenamiento", color="k", size="20pt")
        # Add Axis Labels
        styles = {"color": "k", "font-size": "10pt"}
        self.graphWidget.setLabel("left", "Recompensa media 100 eps", **styles)
        self.graphWidget.setLabel("bottom", "Nº Episodio", **styles)
        # Add legend
        self.graphWidget.addLegend()
        # Add grid
        self.graphWidget.showGrid(x=True, y=True)
        # Set Range
        self.graphWidget.setAutoVisible(y=True, x=True)

    def plot(self, x, y, alg_name, color):
        pen = pg.mkPen(color=color, width=3)
        if self.__referencias_plt[alg_name] is None:
            self.__referencias_plt[alg_name] = self.graphWidget.plot(x, y, name=alg_name, pen=pen)#, symbol='+', symbolSize=30, symbolBrush=(color))
        else:
            self.__referencias_plt[alg_name].setData(x, y)

    def add_plot_data(self, x, y, alg_name):
        if alg_name not in self.plot_data_x:
            self.plot_data_x[alg_name] = []
        for x_ in x:
            self.plot_data_x[alg_name].append(x_)
        if alg_name not in self.plot_data_y:
            self.plot_data_y[alg_name] = []
        for y_ in y:
            self.plot_data_y[alg_name].append(y_)

        self.plot(self.plot_data_x[alg_name], self.plot_data_y[alg_name], alg_name, self.__colores[alg_name])

import random
import matplotlib
matplotlib.use('Qt5Agg')

from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg , NavigationToolbar2QT
from matplotlib.figure import Figure


class VentanaBenchmark(QtWidgets.QMainWindow):

    # class Lienzo(FigureCanvasQTAgg):
    #     def __init__(self, parent=None, width=5, height=4, dpi=100):
    #         fig = Figure(figsize=(width, height), dpi=dpi)
    #         self.axes = fig.add_subplot(111)
    #         super(VentanaBenchmark.Lienzo, self).__init__(fig)

    def anadir_medicion(self, medida):
        print('señal recibida:', medida, 'pasos')
        #self.barra_progreso.setValue((self.barra_progreso.value()+1)/40*100)

    # def cancelar(self):
    #     self.benchmark.terminate()
    #     print('benchmark cancelado')
    #     self.close()
    #
    # def __init__(self, lista_algoritmos, entorno, controlador, alpha, gamma, param1, param2):
    #     super().__init__()
    #
    #
    #     self.lista_algoritmos = lista_algoritmos
    #
    #     self.lienzo = VentanaBenchmark.Lienzo()
    #     toolbar = NavigationToolbar2QT(self.lienzo, self)
    #
    #     layout = QtWidgets.QVBoxLayout()
    #     layout.addWidget(toolbar)
    #     layout.addWidget(self.lienzo)
    #     self.barra_progreso = QtWidgets.QProgressBar()
    #     layout.addWidget(self.barra_progreso)
    #     widget = QtWidgets.QWidget()
    #     widget.setLayout(layout)
    #     self.setCentralWidget(widget)
    #
    #     self.data = dict([])
    #     for alg in self.lista_algoritmos:
    #         self.data[alg] = None
    #     data = [random.random() for _ in range(len(lista_algoritmos))]
    #     self.lienzo.axes.bar(lista_algoritmos, data)
    #
    #     self.lienzo.draw()
    #     self.show()
    #
    #     self.benchmark = ThreadBenchmark(entorno, controlador, EpsilonGreedy,10000,alpha, gamma, param1, param2)
    #     self.benchmark.sig_actualizar_benchmark.connect(self.anadir_medicion)
    #     #self.benchmark.start()

    def __init__(self, lista_algoritmos, entorno, controlador, alpha, gamma, param1, param2):
        super().__init__()

        # self.show()

        self.lista_algoritmos = lista_algoritmos

        datos = [random.uniform(0, 10) for _ in range(len(lista_algoritmos))]
        barset = QBarSet('Pasos hasta fin del entrenamiento')
        barset.append(datos)
        series = QBarSeries()
        series.append(barset)

        tupla_algoritmos = tuple(lista_algoritmos)
        eje_x = QBarCategoryAxis()
        eje_x.append(tupla_algoritmos)
        eje_y = QValueAxis()

        grafico = QChart()
        grafico.addSeries(series)
        grafico.setAnimationOptions(QChart.SeriesAnimations)
        grafico.addAxis(eje_x, Qt.AlignBottom)
        grafico.addAxis(eje_y, Qt.AlignLeft)

        grafico.legend().setVisible(True)

        chartView = QChartView(grafico)
        self.setCentralWidget(chartView)

        self.datos = dict([])
        for alg in self.lista_algoritmos:
            self.datos[alg] = None

        self.show()
        print("Graph showrd")

        benchmark = ThreadBenchmark(entorno, controlador, EpsilonGreedy,10000,alpha, gamma, param1, param2)
        #benchmark.sig_actualizar_benchmark.connect(self.anadir_medicion)
        benchmark.start()
