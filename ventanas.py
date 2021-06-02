import math
import random

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtGui, uic
from PyQt5.QtWidgets import *
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


class VentanaBenchmark(QtWidgets.QMainWindow):
    def __init__(self, lista_algoritmos, ajustes, entorno, controlador, alpha, gamma, param1, param2):
        super().__init__()
        uic.loadUi('ventana_benchmark.ui', self)

        self.lista_algoritmos = lista_algoritmos
        self.entorno = entorno
        self.controlador = controlador
        self.alpha = alpha
        self.gamma = gamma
        self.param1 = param1
        self.param2 = param2

        tupla_algoritmos = tuple(lista_algoritmos)
        eje_x = QBarCategoryAxis()
        eje_x.append(tupla_algoritmos)
        self.eje_y = QValueAxis()
        self.eje_y.setRange(0, 100)

        self.grafico = QChart()
        #self.grafico.addSeries(series)
        self.grafico.setAnimationOptions(QChart.NoAnimation)
        self.grafico.addAxis(eje_x, Qt.AlignBottom)
        self.grafico.addAxis(self.eje_y, Qt.AlignLeft)  # TODO no se muestra
        n_ejecuciones = ajustes[utils.AJUSTES_PARAM_N_EJECUCIONES]
        self.formatear_titulo_gafico(n_ejecuciones)

        self.grafico.legend().setVisible(True)
        self.grafico.legend().setAlignment(Qt.AlignTop)

    def init_grafico(self):
        self.vista_grafico.setChart(self.grafico)

    def actualizar_grafico(self, algoritmo, nuevo_dato):
        """Añade a la barra de algoritmo el nuevo dato"""
        self.datos[algoritmo].append(nuevo_dato)
        self.grafico.removeAllSeries()
        medias = [np.mean(datos) if len(datos) > 0 else 0 for datos in self.datos.values()]
        mejores = [np.min(datos) if len(datos) > 0 else 0 for datos in self.datos.values()]
        peores = [np.max(datos) if len(datos) > 0 else 0 for datos in self.datos.values()]
        self.eje_y.setRange(0, max(max(medias), max(peores)))

        barset_media = QBarSet('Media')
        barset_media.append(medias)
        barset_mejor = QBarSet('Mejor')
        barset_mejor.append(mejores)
        barset_peor = QBarSet('Peor')
        barset_peor.append(peores)
        series = QBarSeries()
        series.append(barset_media)
        series.append(barset_mejor)
        series.append(barset_peor)
        self.grafico.addSeries(series)
        self.init_grafico()

    def limpiar_grafico(self):
        self.grafico.removeAllSeries()
        self.init_grafico()
        self.__init_datos()

    def __init_datos(self):
        self.datos = dict([])
        for alg in self.lista_algoritmos:
            self.datos[alg] = []

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.controlador.deshabilitar_todo(False)  # Antes de cerrar la ventana habilitamos los botones de ventana princ
        self.controlador.cerrar_benchmark()
        event.accept()

    def formatear_titulo_gafico(self, n_ejecuciones):
        self.grafico.setTitle("Pasos hasta el fin del entrenamiento ("+str(n_ejecuciones)+" ejecuciones)")


class VentanaAjustesBenchmark(QWidget):
    def __init__(self, controlador, ajustes, instancias_algoritmos):
        super().__init__()
        print(ajustes)
        self.controlador = controlador
        self.instancias_algoritmos = instancias_algoritmos

        self.setWindowTitle("Configuración banco de pruebas")
        layout_principal = QVBoxLayout()
        # Layout para el numero de ejecuciones
        layout_n_ejec = QHBoxLayout()
        layout_n_ejec.addWidget(QLabel('Número de ejecuciones por algoritmo:'))
        self.spinbox_n_ejec = QSpinBox()
        self.spinbox_n_ejec.setValue(ajustes[utils.AJUSTES_PARAM_N_EJECUCIONES])
        layout_n_ejec.addWidget(self.spinbox_n_ejec)
        layout_principal.addLayout(layout_n_ejec)

        # Layout de los campos de cada algoritmo
        self.alpha_spinboxes = dict([])
        self.gamma_spinboxes = dict([])
        self.param1_spinboxes = dict([])
        self.param2_spinboxes = dict([])
        self.spinboxes = dict([])
        for alg in instancias_algoritmos:
            nombre = alg.get_nombre()
            gb = QGroupBox(nombre)
            form = QFormLayout()

            self.spinboxes[nombre] = dict([])
            for p in ['alpha', 'gamma']:
                self.spinboxes[nombre][p] = QDoubleSpinBox()
                self.spinboxes[nombre][p].setRange(0, 1)
                self.spinboxes[nombre][p].setSingleStep(0.1)
                self.spinboxes[nombre][p].setValue(ajustes[nombre][p])
                form.addRow(p, self.spinboxes[nombre][p])

            rangos = alg.get_rango_parametros()
            nombres_param = alg.get_nombres_parametros()
            for i in range(2):
                p = 'param'+str(i+1)
                self.spinboxes[nombre][p] = QDoubleSpinBox()
                self.spinboxes[nombre][p].setMinimum(rangos[i][0])
                self.spinboxes[nombre][p].setMaximum(rangos[i][1])
                self.spinboxes[nombre][p].setSingleStep(0.1)
                self.spinboxes[nombre][p].setValue(ajustes[nombre][p])
                form.addRow(nombres_param[i], self.spinboxes[nombre][p])

            gb.setLayout(form)
            layout_principal.addWidget(gb)
            self.boton_restablecer = QPushButton('Restablecer')
            self.boton_restablecer.clicked.connect(self.restablecer)
            layout_principal.addWidget(self.boton_restablecer)

        self.setLayout(layout_principal)

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        ajustes = dict([])
        ajustes[utils.AJUSTES_PARAM_N_EJECUCIONES] = self.spinbox_n_ejec.value()
        for alg in self.instancias_algoritmos:
            nombre = alg.get_nombre()
            ajustes[nombre] = dict([])
            for parametro in ['alpha', 'gamma', 'param1', 'param2']:
                ajustes[nombre][parametro] = self.spinboxes[nombre][parametro].value()

        self.controlador.guardar_ajustes_benchmark(ajustes)
        event.accept()

    def restablecer(self):
        self.spinbox_n_ejec.setValue(10)
        for alg in self.instancias_algoritmos:
            nombre = alg.get_nombre()
            self.spinboxes[nombre]['alpha'].setValue(0.1)
            self.spinboxes[nombre]['gamma'].setValue(1)
            defaults = alg.get_parametros_default()
            self.spinboxes[nombre]['param1'].setValue(defaults[0])
            self.spinboxes[nombre]['param2'].setValue(defaults[1])
