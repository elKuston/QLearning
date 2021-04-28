from PyQt5 import QtWidgets, uic
import sys
import time
from Agente import Agente
import frozenLake
from SegundoPlano import SegundoPlano

from politica import EpsilonGreedy, SoftMax, UpperConfidenceBound
from ventanas import VentanaPrincipal, VentanaMetricas
from PyQt5.QtWidgets import QFileDialog
import utils

LOG_BUFFER_DEFAULT_SIZE = 5


episodios = 100000000000000  # Las "rondas" de entrenamiento
recompensa_media = 0.78  # Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
n_episodios_media = 100


class Controlador:
    def __init__(self):


        self.__init_log_buffer(1)
        self.segundo_plano = None
        app = QtWidgets.QApplication(sys.argv)
        self.nombres_mapas = frozenLake.nombres_mapas()
        self.mapas = frozenLake.mapas()
        self.tamanos_mapas = frozenLake.tamanos_mapas()
        self.mapa_default = 0
        entorno = frozenLake.make(self.mapas[self.mapa_default])
        self.agt = Agente(entorno, self)
        self.vista = VentanaPrincipal(self.tamanos_mapas[self.mapa_default], self.agt, app.primaryScreen().size())

        self.nombres_algoritmos = ['Epsilon Greedy', 'SoftMax', 'Upper Confidence Bound (UCB)']
        self.__map_ui()

        self.alpha = 0.1  # Tasa de aprendizaje
        self.gamma = 1  # Determina cuánta importancia tienen las recompensas de los nuevos estados
        self.epsilon = 1  # La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)
        self.variable_param_1 = 0.99  # POR DEFECTO es el epsilon_decay

        self.algoritmos = self.get_algoritmos()

        self.agt.set_politica(self.algoritmos[0])

        self.vista.show()
        #self.vista_metricas = VentanaMetricas()
        #self.vista_metricas.show()
        sys.exit(app.exec_())

    def get_algoritmos(self):
        return [EpsilonGreedy(self.agt, self.epsilon, self.variable_param_1),
                SoftMax(self.agt, 0.5, 0.99),
                UpperConfidenceBound(self.agt, 64, 64 * episodios)]

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
        self.flush_log()
        self.limpiar_log_button = self.vista.limpiarLogButton
        self.exportar_q_button = self.vista.exportarMatrizButton
        self.importar_q_button = self.vista.importarMatrizButton
        self.alpha_spinbox = self.vista.alphaSpinbox
        self.epsilon_spinbox = self.vista.epsilonSpinbox
        self.variable_param_spinbox_1 = self.vista.variableParamSpinbox1
        self.gamma_spinbox = self.vista.gammaSpinbox

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

    #TODO - en la branch correspondiente, meter esto en el módulo utils que aquí sobra un poco
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
        # TODO textos hardcodeados que hay que quitar
        if self.agt.playing:
            text = 'Pause'
        else:
            text = 'Play'
        self.play_pause_button.setText(text)

    def cambiar_tiempo_espera(self):
        self.agt.cambiar_tiempo_espera(
            self.espera_slider.value() / 1000)  # Dividimos entre 1000 porque en la GUI está puesto en ms y aquí lo queremos en s

    def __cancelar_segundo_plano(self):
        if self.segundo_plano is not None:
            self.segundo_plano.terminate()
        self.segundo_plano = None  #TODO esto lo pongo aqui para poder deshabilitar el boton play después de un reset o cuando no haya un entrenamiento en proceso (está feo pero no es funcional,prioridad baja)

    def reset(self):
        self.__cancelar_segundo_plano()
        self.agt.reset()
        if self.agt.playing:
            self.togglePlay()
        self.actualizarVista()

    def entrenar(self):
        self.reset()
        self.segundo_plano = SegundoPlano(self.agt.entrenar, self.alpha, self.gamma, episodios, recompensa_media,
                                          n_episodios_media)
        self.segundo_plano.start()

        if not self.agt.playing:
            self.togglePlay()

    def cambiar_algoritmo(self):
        self.agt.set_politica(self.algoritmos[self.dropdown_algoritmo.currentIndex()])
        self.reset()

    def resolver(self):
        self.__cancelar_segundo_plano()
        self.segundo_plano = SegundoPlano(self.agt.resolver)
        self.segundo_plano.start()

        if not self.agt.playing:
            self.togglePlay()

    def cambiar_mapa(self):
        entorno = frozenLake.make(self.mapas[self.dropdown_mapa.currentIndex()])
        self.agt = Agente(entorno, self)
        self.algoritmos = self.get_algoritmos()
        self.cambiar_algoritmo()
        self.vista.cambiar_entorno(self.tamanos_mapas[self.dropdown_mapa.currentIndex()], self.agt)

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

    # Ventajas de este enfoque (usar properties): El código queda mucho más modularizado y cómodo ya que no hay que
    # estar pendiente de la GUI cada vez que se cambia el valor en el código.
    # Desventaja: que cada vez que se lee el valor se hace una llamada a la GUI, lo cual es bastante ineficiente.
    # En este caso no creo que la eficiencia sea lo más importante, así que me he decantado por esta opción.
    # EDIT: tanto es así que creo que debería TODO cambiar el tiempo de espera entre pasos a una property
    # Aunque de esto último no estoy tan seguro porque esa sí que es una llamada que se realiza miles de veces / segundo

    @property
    def epsilon(self):
        return self.epsilon_spinbox.value()

    @epsilon.setter
    def epsilon(self, new_e):
        self.epsilon_spinbox.setValue(new_e)

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

