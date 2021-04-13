from PyQt5 import QtWidgets, uic
import sys
from Agente import Agente
import frozenLake
from SegundoPlano import SegundoPlano

from politica import EpsilonGreedy, SoftMax, UpperConfidenceBound
from ventanas import VentanaPrincipal, VentanaMetricas

alpha = 0.1  # Tasa de aprendizaje
gamma = 1  # Determina cuánta importancia tienen las recompensas de los nuevos estados
epsilon = 1  # La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)

episodios = 100000000000000  # Las "rondas" de entrenamiento
recompensa_media = 0.78  # Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
n_episodios_media = 100


class Controlador:
    def __init__(self):
        self.segundo_plano = None
        app = QtWidgets.QApplication(sys.argv)
        self.nombres_mapas = ['4x4', '8x8']
        self.mapas = ['FrozenLake-v0', 'FrozenLake8x8-v0']
        self.tamanos_mapas = [4, 8]
        self.mapa_default = 0
        entorno = frozenLake.make(self.mapas[self.mapa_default])
        self.agt = Agente(entorno, self)
        self.algoritmos = self.get_algoritmos()
        self.nombres_algoritmos = ['Epsilon Greedy', 'SoftMax', 'Upper Confidence Bound (UCB)']

        self.agt.set_politica(self.algoritmos[0])
        self.vista = VentanaPrincipal(self.tamanos_mapas[self.mapa_default], self.agt)

        self.__map_ui()

        self.vista.show()
        self.vista_metricas = VentanaMetricas()
        self.vista_metricas.show()
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
        self.segundo_plano = SegundoPlano(self.agt.entrenar, alpha, gamma, episodios, recompensa_media,
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
        if self.log_box is not None:
            self.log_box.append(text)
        #if self.was_max:
        self.log_box.verticalScrollBar().setValue(self.log_box.verticalScrollBar().maximum())
