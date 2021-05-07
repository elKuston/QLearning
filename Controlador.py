from PyQt5 import QtWidgets, uic
import sys
import time
from Agente import Agente
import frozenLake

from politica import EpsilonGreedy, SoftMax, UpperConfidenceBound
from ventanas import VentanaPrincipal, VentanaMetricas
from threadsSegundoPlano import *
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import pyqtSignal, QObject
import utils

LOG_BUFFER_DEFAULT_SIZE = 5
ENTRENANDO = 0
RESOLVIENDO = 1

alpha = 0.1  # Tasa de aprendizaje
gamma = 1  # Determina cuánta importancia tienen las recompensas de los nuevos estados
epsilon = 1  # La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)

episodios = 100000000000000  # Las "rondas" de entrenamiento
recompensa_media = 0.78  # Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
n_episodios_media = 100


class Controlador(QObject):

    sig_cambiar_tiempo_espera = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.__init_log_buffer(1)
        self.accion_actual = ENTRENANDO
        self.thread_entrenamiento = None
        self.thread_resolucion = None
        app = QtWidgets.QApplication(sys.argv)
        self.nombres_mapas = frozenLake.nombres_mapas()
        self.mapas = frozenLake.mapas()
        self.tamanos_mapas = frozenLake.tamanos_mapas()
        self.mapa_default = 0
        entorno = frozenLake.make(self.mapas[self.mapa_default])
        self.agt = Agente(entorno, self)
        self.algoritmos = self.get_algoritmos()
        self.nombres_algoritmos = ['Epsilon Greedy', 'SoftMax', 'Upper Confidence Bound (UCB)']

        self.agt.set_politica(self.algoritmos[0])
        self.vista = VentanaPrincipal(self.tamanos_mapas[self.mapa_default], self.agt, app.primaryScreen().size())

        self.__map_ui()

        self.vista.show()
        #self.vista_metricas = VentanaMetricas()
        #self.vista_metricas.show()
        sys.exit(app.exec_())

    def get_algoritmos(self):
        return [EpsilonGreedy(self.agt, epsilon, 0.9),
                SoftMax(self.agt, 0.5, 0.99),
                UpperConfidenceBound(self.agt, 64, 64 * episodios)]

    def __map_ui(self):
        """
        Cogemos todos los componentes de la vista y los guardamos como variables locales del controlador. Duplicamos espacio en memoria pero es mucho mas comodo y total tampoco estamos en los 90 con 64kb de ram xd
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
        self.flush_log()
        self.limpiar_log_button = self.vista.limpiarLogButton
        self.exportar_q_button = self.vista.exportarMatrizButton
        self.importar_q_button = self.vista.importarMatrizButton

        # Mapeamos cada widget con su comportamiento
        self.play_pause_button.clicked.connect(self.togglePlay)
        self.espera_slider.valueChanged.connect(self.cambiar_tiempo_espera)
        self.reset_button.clicked.connect(self.reset)
        self.entrenar_button.clicked.connect(self.entrenar)
        self.dropdown_algoritmo.addItems(self.nombres_algoritmos)
        self.dropdown_algoritmo.currentIndexChanged.connect(self.cambiar_algoritmo)
        self.resolver_button.clicked.connect(self.resolver)
        self.dropdown_mapa.addItems(self.nombres_mapas)
        self.dropdown_mapa.setCurrentIndex(self.mapa_default)
        self.dropdown_mapa.currentIndexChanged.connect(self.cambiar_mapa)
        self.limpiar_log_button.clicked.connect(self.limpiar_log_box)
        self.exportar_q_button.clicked.connect(self.abrir_dialogo_guardado)
        self.importar_q_button.clicked.connect(self.abrir_dialogo_lectura)

    def abrir_dialogo_guardado(self):
        opciones = QFileDialog.Options()
        mapa_actual = self.dropdown_mapa.currentIndex()
        extension = utils.FORMATO_FICHERO+str(self.tamanos_mapas[mapa_actual])

        tam = self.nombres_mapas[mapa_actual]
        # TODO texto hardcodeado
        file = QFileDialog.getSaveFileName(self.vista,
                                           'Exportar Matriz Q',
                                           'matriz'+extension,
                                           'Policy file '+tam+' (*'+extension+')',
                                           options=opciones)
        nombre_fichero = file[0]
        if len(nombre_fichero) > 0:
            if not nombre_fichero.endswith(extension):
                nombre_fichero += utils.FORMATO_FICHERO
            print(nombre_fichero)
            utils.guardar_matriz_Q(nombre_fichero, self.agt.readonly_Q)  # TODO replace with readonly_q
            self.print_log('Fichero exportado con éxito en '+nombre_fichero)

    def abrir_dialogo_lectura(self):
        opciones = QFileDialog.Options()
        mapa_actual = self.dropdown_mapa.currentIndex()
        extension = utils.FORMATO_FICHERO+str(self.tamanos_mapas[mapa_actual])
        tam = self.nombres_mapas[mapa_actual]

        file = QFileDialog.getOpenFileName(self.vista, 'Importar Matriz Q',
                                           'Default File',
                                           'Policy file '+tam+' (*'+extension+')',
                                           options=opciones)
        nombre_fichero = file[0]
        if len(nombre_fichero) > 0:
            Q = utils.leer_matriz_Q(nombre_fichero)
            self.print_log('Fichero importado con éxito desde '+nombre_fichero)
            self.agt.Q = Q  # TODO MEGAUNSAFE pero bueno poquito a poquito
            self.actualizarVista()

    def actualizarVista(self):
        self.vista.update()

    def paso(self):
        print("paso")

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
            self.espera_slider.value()/1000  # Dividimos entre 1000 porque en la GUI está puesto en ms y aquí lo queremos en s
        )
        #self.agt.cambiar_tiempo_espera(
         #   self.espera_slider.value() / 1000)  # Dividimos entre 1000 porque en la GUI está puesto en ms y aquí lo queremos en s

    def reset(self):
        #self.__cancelar_segundo_plano()
        if self.agt.playing:
            self.togglePlay()
        if self.get_thread_actual() is not None:
            self.get_thread_actual().terminate()

        self.algoritmos = self.get_algoritmos()
        self.agt.reset()
        self.generar_thread_actual()
        self.actualizarVista()

        self.print_log("Reset...")

    def generar_thread_actual(self):
        thread = None
        if self.accion_actual == ENTRENANDO:
            self.thread_entrenamiento = ThreadEntrenamiento(self, self.agt, alpha, gamma, episodios,
                                                            recompensa_media, n_episodios_media)
            thread = self.thread_entrenamiento
        elif self.accion_actual == RESOLVIENDO:
            self.thread_resolucion = ThreadEjecucion(self, self.agt)
            thread = self.thread_resolucion
        else:
            raise ValueError("El valor de la accion actual {} no es valido".format(self.accion_actual))

        thread.sig_actualizar_vista.connect(self.actualizarVista)
        thread.sig_print.connect(self.print_log)
        self.cambiar_tiempo_espera()
        return thread

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
        #self.reset()
        self.accion_actual = ENTRENANDO
        if self.get_thread_inactivo() is not None:
            self.get_thread_inactivo().terminate()
        self.get_thread_actual().start()


        if not self.agt.playing:
            self.togglePlay()

    def get_thread_inactivo(self):
        thread = None
        if self.accion_actual == RESOLVIENDO:
            thread = self.thread_entrenamiento
        elif self.accion_actual == ENTRENANDO:
            thread = self.thread_resolucion
        return thread


    def cambiar_algoritmo(self):
        self.agt.set_politica(self.algoritmos[self.dropdown_algoritmo.currentIndex()])
        self.reset()

    def resolver(self):
        self.accion_actual = RESOLVIENDO
        #self.__cancelar_segundo_plano()
        #self.segundo_plano = SegundoPlano(self.agt.resolver)
        #self.segundo_plano.start()
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

    def print_log(self, text):
        print(text)
        self.__add_to_log_buffer(text)
        # TODO - Hacer que no baje abajo si no estaba antes abajo (es decir, si el user lo ha movido para mirar algo)
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())

    def limpiar_log_box(self):
        self.log_box.setText('')

    def __init_log_buffer(self, buffer_size=LOG_BUFFER_DEFAULT_SIZE):
        self.log_buffer = []
        self.buffer_size = buffer_size

    def __add_to_log_buffer(self, text):
        self.log_buffer.append(text)
        if self.__log_buffer_full():
            self.__clear_log_buffer()

    def __log_buffer_full(self):
        return len(self.log_buffer) == self.buffer_size

    def __clear_log_buffer(self):
        full_log = '\n'.join(self.log_buffer)
        self.log_box.append(full_log)
        self.__init_log_buffer(self.buffer_size)

    def flush_log(self):
        self.__clear_log_buffer()
