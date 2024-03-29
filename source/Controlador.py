import sys
import time
from Agente import Agente

from typing import Type
from politica import Politica, EpsilonGreedy, UpperConfidenceBound
from ventanas import *
from threadsSegundoPlano import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject, QSettings
import utils

ENTRENANDO = 0
RESOLVIENDO = 1


episodios = 100000000000000  # Las "rondas" de entrenamiento
recompensa_media = 0.78  # Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
n_episodios_media = 100


class Controlador(QObject):
    sig_cambiar_tiempo_espera = pyqtSignal(float)

    def __init__(self, algoritmo_base: Type[Politica] = EpsilonGreedy):
        """
        Inicializa y prepara los componentes para que se puedan registrar los algoritmos.
        Requiere al menos un algoritmo para poder iniciar la vista etc.
        En este caso, se usará por defecto EpsilonGreedy"""

        super().__init__()
        self.algoritmos_registrados = []  # Almacena las CLASES de los algoritmos
        #self.__init_log_buffer(1)
        self.accion_actual = ENTRENANDO
        self.thread_entrenamiento = None
        self.thread_resolucion = None
        self.app = QtWidgets.QApplication(sys.argv)
        self.nombres_mapas = frozenLake.nombres_mapas()
        self.mapas = frozenLake.mapas()
        self.tamanos_mapas = frozenLake.tamanos_mapas()
        self.mapa_default = 0
        entorno = frozenLake.make(self.mapas[self.mapa_default])
        self.agt = Agente(entorno, self)
        self.vista = VentanaPrincipal(self.tamanos_mapas[self.mapa_default], self.agt, self.app.primaryScreen().size())

        self.__map_ui()

        self.registrar_algoritmo(algoritmo_base)
        self.__map_comportamiento_ui()

        self.alpha = 0.5  # Tasa de aprendizaje
        self.gamma = 1  # Determina cuánta importancia tienen las recompensas de los nuevos estados
        self.variable_param_1 = 1  # La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)
        self.variable_param_2 = 0.99  # POR DEFECTO es el epsilon_decay
        self.algoritmos = []

    def cargar_ajustes_benchmark(self):
        self.ajustes_benchmark = QSettings(utils.NOMBRE_APP, utils.NOMBRE_MODULO_SETTINGS)
        self.ajustes_benchmark_dict = utils.formatear_ajustes_benchmark(self.ajustes_benchmark, self.get_algoritmos(), self)

    def start(self):
        """Una vez registrados los algoritmos, este método termina de configurar los componentes e inicia la vista"""
        self.algoritmos = self.get_algoritmos()  # Almacena las INSTANCIAS de los algoritmos

        self.agt.set_politica(self.algoritmos[0])

        # benchmark
        self.benchmark_running = False
        self.benchmark = None
        self.ajustes_benchmark_dict = dict([])
        self.cargar_ajustes_benchmark()

        self.vista.show()
        self.vista_metricas = VentanaMetricasPyqtgraph(self.get_nombres_algoritmos())
        self.vista_benchmark = VentanaBenchmark(self.get_nombres_algoritmos(), self.ajustes_benchmark_dict,
                                                self.agt.entorno, self, )

        sys.exit(self.app.exec_())

    def mostrar_metricas(self):
        self.vista_metricas.show()

    def mostrar_benchmark(self):
        self.deshabilitar_todo(True)
        self.vista_benchmark.show()
        self.boton_iniciar_benchmark = self.vista_benchmark.startStopButton
        self.barra_progreso_benchmark = self.vista_benchmark.progressBar
        self.descripcion_progreso_benchmark = self.vista_benchmark.progressLabel

        self.boton_iniciar_benchmark.clicked.connect(self.toggle_benchmark)
        self.vista_benchmark.init_grafico()

        self.vista_benchmark.actionConfiguracion.triggered.connect(self.mostrar_ajustes_benchmark)

    def mostrar_ajustes_benchmark(self):
        ajustes = utils.formatear_ajustes_benchmark(self.ajustes_benchmark, self.get_algoritmos(), self)
        self.vista_ajustes_bechmark = VentanaAjustesBenchmark(self, ajustes, self.get_algoritmos())
        self.vista_ajustes_bechmark.show()

    def guardar_ajustes_benchmark(self, ajustes):
        self.ajustes_benchmark_dict = ajustes  # Actualizamos los ajustes del controlador
        self.vista_benchmark.set_ajustes(ajustes)
        utils.guardar_ajustes_benchmark(self.ajustes_benchmark, ajustes, self.get_algoritmos())

    def cerrar_benchmark(self):
        if self.benchmark is not None:
            self.benchmark.terminate()
        self.boton_iniciar_benchmark.setText('Iniciar')
        self.vista_benchmark.limpiar_grafico()
        self.barra_progreso_benchmark.setValue(0)
        self.play_pause_button.setDisabled(True)
        self.entrenar_button.setDisabled(True)

    def toggle_benchmark(self):
        if self.benchmark_running:
            self.benchmark_running = False
            self.boton_iniciar_benchmark.setText('Iniciar')
            self.descripcion_progreso_benchmark.setText('Benchmark detenido')
            self.barra_progreso_benchmark.setValue(0)
            self.benchmark.terminate()
        else:
            self.benchmark_running = True
            self.boton_iniciar_benchmark.setText('Detener')
            self.vista_benchmark.limpiar_grafico()
            self.mediciones_benchmark = dict([])
            for n in self.get_nombres_algoritmos():
                self.mediciones_benchmark[n] = []

            self.benchmark = ThreadBenchmark(self.agt.entorno, self, self.algoritmos_registrados, 10000,
                                             self.ajustes_benchmark_dict)
            self.benchmark.sig_actualizar_benchmark.connect(self.anadir_medicion_benchmark)
            self.benchmark.start()

            self.descripcion_progreso_benchmark.setText('Iniciando benchmark...')

    def deshabilitar_todo(self, deshabilitado):
        self.entrenar_button.setDisabled(deshabilitado)
        self.reset_button.setDisabled(deshabilitado)
        self.play_pause_button.setDisabled(deshabilitado)
        self.resolver_button.setDisabled(deshabilitado)
        self.dropdown_mapa.setDisabled(deshabilitado)
        self.dropdown_algoritmo.setDisabled(deshabilitado)
        self.habilitar_hiperparams(not deshabilitado)

    def anadir_medicion_benchmark(self, politica, medida):
        self.mediciones_benchmark[politica].append(medida)
        ejecuciones_totales = self.ajustes_benchmark_dict[
                                  utils.AJUSTES_PARAM_N_EJECUCIONES] * len(self.algoritmos_registrados)
        ejecuciones_completadas = sum([len(self.mediciones_benchmark[p]) for p in self.get_nombres_algoritmos()])
        progreso = 100.0*ejecuciones_completadas/ejecuciones_totales
        self.barra_progreso_benchmark.setValue(progreso)
        self.descripcion_progreso_benchmark.setText(
            'Ejecutado: {} ({}/{})'.format(politica,
                                           len(self.mediciones_benchmark[politica]),
                                           self.ajustes_benchmark_dict[utils.AJUSTES_PARAM_N_EJECUCIONES])
        )
        if progreso == 100:
            self.descripcion_progreso_benchmark.setText('Benchmark finalizado')
        self.vista_benchmark.actualizar_grafico(politica, medida)

    def get_algoritmos(self):
        algoritmos = []
        for alg in self.algoritmos_registrados:
            algoritmos.append(alg(self.agt, self.variable_param_1, self.variable_param_2))
        return algoritmos

    def registrar_algoritmo(self, clase: Type[Politica], recargar_dropdown=True):
        self.algoritmos_registrados.append(clase)
        if recargar_dropdown:
            self.recargar_dropdown()

    def get_nombres_algoritmos(self):
        return [alg.get_nombre() for alg in self.get_algoritmos()]

    def recargar_dropdown(self):
        nombres_algoritmos = self.get_nombres_algoritmos()
        self.dropdown_algoritmo.clear()
        self.dropdown_algoritmo.addItems(nombres_algoritmos)
        self.dropdown_algoritmo.currentIndexChanged.connect(self.cambiar_algoritmo)

    def __map_ui(self):
        """
        Cogemos todos los componentes de la vista y los guardamos como variables locales del controlador.
        Duplicamos espacio en memoria pero es mucho mas comodo y total tampoco estamos en los 90 con 64kb de ram xd
        """
        # Convertimos las variables de la vista a variables locales
        self.play_pause_button = self.vista.playButton
        self.espera_slider = self.vista.esperaSlider
        self.reset_button = self.vista.resetButton
        self.entrenar_button = self.vista.entrenarButton
        self.dropdown_algoritmo = self.vista.dropdownAlgoritmo
        self.resolver_button = self.vista.resolverButton
        self.dropdown_mapa = self.vista.dropdownMapa
        self.log_box = self.vista.logTextbox
        self.print_log('Q-Learning')
        #self.limpiar_log_button = self.vista.limpiarLogButton
        self.limpiar_log_action = self.vista.limpiarLogAction
        #self.exportar_q_button = self.vista.exportarMatrizButton
        #self.importar_q_button = self.vista.importarMatrizButton
        #  Reemplazado por los dos de abajo (menu de barra superior en vez de botones)
        self.exportar_q_action = self.vista.exportarMatrizAction
        self.importar_q_action = self.vista.importarMatrizAction
        self.alpha_spinbox = self.vista.alphaSpinbox
        self.gamma_spinbox = self.vista.gammaSpinbox
        self.variable_param_spinbox_1 = self.vista.variableParamSpinbox1
        self.variable_param_spinbox_2 = self.vista.variableParamSpinbox2
        self.variable_param_label_1 = self.vista.variableParamLabel1
        self.variable_param_label_2 = self.vista.variableParamLabel2
        self.mostrar_metricas_action = self.vista.mostrarMetricasAction
        self.mostrar_benchmark_action = self.vista.abrirBenchmarkAction

    def __map_comportamiento_ui(self):
        # Mapeamos cada widget con su comportamiento
        self.play_pause_button.clicked.connect(self.togglePlay)
        self.espera_slider.valueChanged.connect(self.cambiar_tiempo_espera)
        self.reset_button.clicked.connect(self.reset)
        self.entrenar_button.clicked.connect(self.entrenar)
        #self.recargar_dropdown()
        self.resolver_button.clicked.connect(self.resolver)
        self.dropdown_mapa.addItems(self.nombres_mapas)
        self.dropdown_mapa.setCurrentIndex(self.mapa_default)
        self.dropdown_mapa.currentIndexChanged.connect(self.cambiar_mapa)
        #self.limpiar_log_button.clicked.connect(self.limpiar_log_box)
        self.limpiar_log_action.triggered.connect(self.limpiar_log_box)
        #self.exportar_q_button.clicked.connect(self.abrir_dialogo_guardado)
        #self.importar_q_button.clicked.connect(self.abrir_dialogo_lectura)
        #  Reemplazado por los dos de abajo (menu de barra superior en vez de botones)
        self.exportar_q_action.triggered.connect(self.abrir_dialogo_guardado)
        self.importar_q_action.triggered.connect(self.abrir_dialogo_lectura)
        self.alpha_spinbox.valueChanged.connect(self.refresh_algoritmo)
        self.gamma_spinbox.valueChanged.connect(self.refresh_algoritmo)
        self.variable_param_spinbox_1.valueChanged.connect(self.refresh_algoritmo)
        self.variable_param_spinbox_2.valueChanged.connect(self.refresh_algoritmo)
        self.mostrar_metricas_action.triggered.connect(self.mostrar_metricas)
        self.mostrar_benchmark_action.triggered.connect(self.mostrar_benchmark)

    # TODO - en la branch correspondiente, meter esto en el módulo utils que aquí sobra un poco
    def abrir_dialogo_guardado(self):
        opciones = QFileDialog.Options()
        mapa_actual = self.dropdown_mapa.currentIndex()
        extension = utils.FORMATO_FICHERO + str(self.tamanos_mapas[mapa_actual])

        tam = self.nombres_mapas[mapa_actual]
        # TODO texto hardcodeado
        file = QFileDialog.getSaveFileName(self.vista,
                                           'Exportar Matriz Q',
                                           'matriz' + extension,
                                           'Policy file ' + tam + ' (*' + extension + ')',
                                           options=opciones)
        nombre_fichero = file[0]
        if len(nombre_fichero) > 0:
            if not nombre_fichero.endswith(extension):
                nombre_fichero += utils.FORMATO_FICHERO
            print(nombre_fichero)
            utils.guardar_matriz_Q(nombre_fichero, self.agt.readonly_Q)
            self.print_log('Fichero exportado con éxito en ' + nombre_fichero)

    def abrir_dialogo_lectura(self):
        opciones = QFileDialog.Options()
        mapa_actual = self.dropdown_mapa.currentIndex()
        extension = utils.FORMATO_FICHERO + str(self.tamanos_mapas[mapa_actual])
        tam = self.nombres_mapas[mapa_actual]

        file = QFileDialog.getOpenFileName(self.vista, 'Importar Matriz Q',
                                           'Default File',
                                           'Policy file ' + tam + ' (*' + extension + ')',
                                           options=opciones)
        nombre_fichero = file[0]
        if len(nombre_fichero) > 0:
            Q = utils.leer_matriz_Q(nombre_fichero)
            self.print_log('Fichero importado con éxito desde ' + nombre_fichero)
            self.agt.Q = Q  # TODO MEGAUNSAFE pero bueno poquito a poquito
            self.actualizarVista()

    def actualizarVista(self):
        self.vista.update()

    def togglePlay(self):
        self.agt.toggle_play()
        if self.get_thread_actual() is not None:
            if self.agt.playing:
                self.get_thread_actual().start()
            else:
                self.get_thread_actual().terminate()

        # TODO textos hardcodeados que hay que quitar
        if self.agt.playing:
            text = 'Pause'
        else:
            text = 'Play'
        self.play_pause_button.setText(text)

    def cambiar_tiempo_espera(self):
        self.sig_cambiar_tiempo_espera.emit(
            self.espera_slider.value() / 1000
            # Dividimos entre 1000 porque en la GUI está puesto en ms y aquí lo queremos en s
        )

    def hiperparams_default(self):
        params = self.agt.politica.get_parametros_default()
        self.variable_param_spinbox_1.setValue(params[0])
        self.variable_param_spinbox_2.setValue(params[1])

    def reset(self):
        if self.agt.playing:
            self.togglePlay()
        if self.get_thread_actual() is not None:
            self.get_thread_actual().terminate()

        self.refresh_algoritmo()
        self.agt.reset()
        self.generar_thread_actual()
        self.habilitar_hiperparams()
        self.mostrar_benchmark_action.setDisabled(False)
        self.entrenar_button.setDisabled(False)
        self.play_pause_button.setDisabled(True)
        self.resolver_button.setDisabled(True)
        self.hiperparams_default()
        self.actualizarVista()

        self.print_log("Reset...")

    def habilitar_hiperparams(self, habilitados=True):
        self.alpha_spinbox.setDisabled(not habilitados)
        self.gamma_spinbox.setDisabled(not habilitados)
        self.variable_param_spinbox_1.setDisabled(not habilitados)
        self.variable_param_spinbox_2.setDisabled(not habilitados)

    def generar_thread_actual(self):
        thread = None
        if self.accion_actual == ENTRENANDO:
            self.thread_entrenamiento = ThreadEntrenamiento(self, self.agt, self.alpha, self.gamma, episodios,
                                                            recompensa_media, n_episodios_media)
            thread = self.thread_entrenamiento
        elif self.accion_actual == RESOLVIENDO:
            self.thread_resolucion = ThreadEjecucion(self, self.agt)
            thread = self.thread_resolucion
        else:
            raise ValueError("El valor de la accion actual {} no es valido".format(self.accion_actual))

        thread.sig_actualizar_vista.connect(self.actualizarVista)
        thread.sig_print.connect(self.print_log)
        if isinstance(thread, ThreadEntrenamiento):
            thread.sig_plot.connect(self.add_plot_data)
            thread.sig_fin_entrenamiento.connect(self.fin_entrenamiento)
        self.cambiar_tiempo_espera()
        return thread

    def fin_entrenamiento(self):
        self.play_pause_button.setDisabled(True)
        self.resolver_button.setDisabled(False)

    def add_plot_data(self, x, y):
        self.vista_metricas.add_plot_data(x, y, self.agt.politica.get_nombre())

    def get_thread_actual(self):
        thread = None
        if self.accion_actual == ENTRENANDO:
            thread = self.thread_entrenamiento
        elif self.accion_actual == RESOLVIENDO:
            thread = self.thread_resolucion
        if thread is None:
            thread = self.generar_thread_actual()
        return thread

    def entrenar(self):
        self.accion_actual = ENTRENANDO
        if self.get_thread_inactivo() is not None:
            self.get_thread_inactivo().terminate()
        self.get_thread_actual().start()

        if not self.agt.playing:
            self.togglePlay()
        self.habilitar_hiperparams(False)
        self.mostrar_benchmark_action.setDisabled(True)
        self.entrenar_button.setDisabled(True)
        self.play_pause_button.setDisabled(False)

    def get_thread_inactivo(self):
        thread = None
        if self.accion_actual == RESOLVIENDO:
            thread = self.thread_entrenamiento
        elif self.accion_actual == ENTRENANDO:
            thread = self.thread_resolucion
        return thread

    def refresh_algoritmo(self):
        self.algoritmos = self.get_algoritmos()
        self.agt.set_politica(self.algoritmos[self.dropdown_algoritmo.currentIndex()])

    def cambiar_nombre_hiperparams(self):
        nombres = self.agt.politica.get_nombres_parametros()
        self.variable_param_label_1.setText(nombres[0])
        self.variable_param_label_2.setText(nombres[1])
        es_ucb = isinstance(self.agt.politica, UpperConfidenceBound)
        self.alpha_spinbox.setDisabled(es_ucb)
        self.gamma_spinbox.setDisabled(es_ucb)

    def cambiar_rango_hiperparams(self):
        rangos = self.agt.politica.get_rango_parametros()
        self.variable_param_spinbox_1.setMinimum(rangos[0][0])
        self.variable_param_spinbox_1.setMaximum(rangos[0][1])
        self.variable_param_spinbox_2.setMinimum(rangos[1][0])
        self.variable_param_spinbox_2.setMaximum(rangos[1][1])

    def cambiar_algoritmo(self):
        self.refresh_algoritmo()
        self.cambiar_nombre_hiperparams()
        self.cambiar_rango_hiperparams()
        self.reset()

    def resolver(self):
        self.accion_actual = RESOLVIENDO
        if self.get_thread_inactivo() is not None:
            self.get_thread_inactivo().terminate()
        self.get_thread_actual().start()

        if not self.agt.playing:
            self.togglePlay()

    def cambiar_mapa(self):
        entorno = frozenLake.make(self.mapas[self.dropdown_mapa.currentIndex()])
        self.agt = Agente(entorno, self)
        self.algoritmos = self.get_algoritmos()
        self.cambiar_algoritmo()
        self.vista.cambiar_entorno(self.tamanos_mapas[self.dropdown_mapa.currentIndex()], self.agt)
        self.reset()

    def print_log(self, text, echo=False):
        if echo:
            print(text)
        estaba_abajo = self.log_box.verticalScrollBar().value() == self.log_box.verticalScrollBar().maximum()
        self.log_box.append(text)
        if estaba_abajo:
            self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def limpiar_log_box(self):
        self.log_box.setText('')

    # Ventajas de este enfoque (usar properties): El código queda mucho más modularizado y cómodo ya que no hay que
    # estar pendiente de la GUI cada vez que se cambia el valor en el código.
    # Desventaja: que cada vez que se lee el valor se hace una llamada a la GUI, lo cual es bastante ineficiente.
    # En este caso no creo que la eficiencia sea lo más importante, así que me he decantado por esta opción.
    # EDIT: tanto es así que creo que debería TODO cambiar el tiempo de espera entre pasos a una property
    # Aunque de esto último no estoy tan seguro porque esa sí que es una llamada que se realiza miles de veces / segundo

    @property
    def alpha(self):
        return self.alpha_spinbox.value()

    @alpha.setter
    def alpha(self, new_a):
        self.alpha_spinbox.setValue(new_a)

    @property
    def gamma(self):
        return self.gamma_spinbox.value()

    @gamma.setter
    def gamma(self, new_g):
        self.gamma_spinbox.setValue(new_g)

    @property
    def variable_param_1(self):
        return self.variable_param_spinbox_1.value()

    @variable_param_1.setter
    def variable_param_1(self, new_val):
        self.variable_param_spinbox_1.setValue(new_val)

    @property
    def variable_param_2(self):
        return self.variable_param_spinbox_2.value()

    @variable_param_2.setter
    def variable_param_2(self, new_e):
        self.variable_param_spinbox_2.setValue(new_e)


