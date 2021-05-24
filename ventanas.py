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
from PyQt5.QtCore import QThread, QObject


class VentanaMetricas(QtWidgets.QMainWindow):

    class Canvas(FigureCanvasQTAgg):
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = fig.add_subplot(111)
            super(VentanaMetricas.Canvas, self).__init__(fig)

    class PlotThread(QObject):
        def __init__(self, lienzo, x, y, plot_refs, alg):
            super().__init__()
            self.lienzo = lienzo
            self.x = x
            self.y = y
            self.plot_refs = plot_refs
            self.alg = alg

        def plot(self):
            if self.plot_refs[self.alg] is None:
                refs = self.lienzo.axes.plot(self.x, self.y, label=self.alg)
                self.plot_refs[self.alg] = refs[0]
            else:
                self.plot_refs[self.alg].set_xdata(self.x)
                self.plot_refs[self.alg].set_ydata(self.y)

            self.lienzo.axes.set_xlim(0, max(self.x)+10)
            self.lienzo.axes.legend(loc='lower right')
            self.lienzo.draw()


    def __init__(self, lista_algoritmos):
        super().__init__()
        self.lista_algoritmos = lista_algoritmos
        self.plot_thread = QThread()
        self.lienzo = VentanaMetricas.Canvas(self, width=5, height=4, dpi=100)
        toolbar = NavigationToolbar(self.lienzo, self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.lienzo)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

        self.show()


        plt.style.use('fivethirtyeight')

        self.lienzo.axes.set_title('Tíulo PROVISIONAL')
        self.lienzo.axes.set_xlabel('Nº episodio')
        self.lienzo.axes.set_ylabel('Recompensa media')

        self.__referencias_plt = dict([])
        self.plot_data_x = dict([])
        self.plot_data_y = dict([])

        for alg in lista_algoritmos:
            self.__referencias_plt[alg] = None
            self.plot_data_x[alg] = []
            self.plot_data_y[alg] = []

    def add_plot_data(self, x, y, alg_name):
        if alg_name not in self.plot_data_x:
            self.plot_data_x[alg_name] = []
        for x_ in x:
            self.plot_data_x[alg_name].append(x_)
        if alg_name not in self.plot_data_y:
            self.plot_data_y[alg_name] = []
        for y_ in y:
            self.plot_data_y[alg_name].append(y_)

        # self.lienzo.axes.cla()
        # for alg in self.lista_algoritmos:
        #     if self.__referencias_plt[alg] is None:
        #         refs = self.lienzo.axes.plot(self.plot_data_x[alg], self.plot_data_y[alg], label=alg)
        #         self.__referencias_plt[alg] = refs[0]
        #     else:
        #         self.__referencias_plt[alg].set_data(self.plot_data_x[alg], self.plot_data_y[alg])
        #
        # self.lienzo.axes.set_xlim(0, max(x))
        # self.lienzo.axes.set_ylim(-1, max(0.2, max(y)+0.1))
        # self.lienzo.axes.legend(loc='lower right')
        # self.lienzo.draw()



        plotter = VentanaMetricas.PlotThread(self.lienzo, self.plot_data_x[alg_name], self.plot_data_y[alg_name],
                                             self.__referencias_plt, alg_name)
        plotter.moveToThread(self.plot_thread)
        plotter.plot()
        #plotter.start()

from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import colorsys

import numpy as np
import utils



class VentanaMetricasPyqtgraph(QtWidgets.QMainWindow):
    def __init__(self, lista_algoritmos):
        super().__init__()
        HSV_tuples = [(x*1.0/len(lista_algoritmos), 0.5, 0.5) for x in range(len(lista_algoritmos))]
        RGB_tuples = list(map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples))

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

        print(self.__colores)

        for alg in lista_algoritmos:
            self.__referencias_plt[alg] = None
            print(alg, self.__colores[alg])
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
