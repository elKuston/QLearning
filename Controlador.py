from PyQt5 import QtWidgets, uic
import sys
from entornoWidget import EntornoWidget
import qlearning
import numpy as np
from Agente import Agente
import gym
from SegundoPlano import SegundoPlano
from PyQt5.QtCore import QThreadPool

from politica import EpsilonGreedy, SoftMax, UpperConfidenceBound
from ventanaPrincipal import VentanaPrincipal

alpha = 0.1  # Tasa de aprendizaje
gamma = 1  # Determina cuánta importancia tienen las recompensas de los nuevos estados
epsilon = 1  # La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)

episodios = 10000 # Las "rondas" de entrenamiento
recompensa_media = 0.78  # Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
n_episodios_media = 100


class Controlador():
    def __init__(self):
        self.thread_pool = QThreadPool()
        self.segundo_plano = None
        app = QtWidgets.QApplication(sys.argv)
        entorno = gym.make(qlearning.nombre_entorno)
        self.agt = Agente(entorno, self)
        self.agt.set_politica(EpsilonGreedy(self.agt, epsilon, 0.9))
        self.vista = VentanaPrincipal(8, self.agt)

        self.__map_buttons()
        self.play_pause_button.clicked.connect(self.togglePlay)
        self.espera_slider.valueChanged.connect(self.cambiar_tiempo_espera)
        self.reset_button.clicked.connect(self.reset)
        self.entrenar_button.clicked.connect(self.entrenar)

        #self.vista = EntornoWidget(8, agt)
        self.vista.show()
        print("ENTRENAMIENTO FINALIZADO")
        # sp = SegundoPlano(agt.resolver)
        #tp.start(sp)
        sys.exit(app.exec_())

    def __map_buttons(self):
        '''
        Cogemos todos los componentes de la vista y los guardamos como variables locales del controlador. Duplicamos espacio en memoria pero es mucho mas comodo y total tampoco estamos en los 90 con 64kb de ram xd
        '''

        self.play_pause_button = self.vista.playButton
        self.espera_slider = self.vista.esperaSlider
        self.reset_button = self.vista.resetButton
        self.entrenar_button = self.vista.entrenarButton

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
        self.agt.cambiar_tiempo_espera(self.espera_slider.value()/1000)  #Dividimos entre 1000 porque en la GUI está puesto en ms y aquí o queremos en s

    def reset(self):
        self.agt.reset()
        if self.agt.playing:
            self.togglePlay()

    def entrenar(self):
        if self.thread_pool.activeThreadCount()>0:  #Si segundo plano ya esta ejecutandose
            self.thread_pool.cancel(self.segundo_plano)
        self.segundo_plano = SegundoPlano(self.agt.entrenar, alpha, gamma, episodios, recompensa_media, n_episodios_media)
        # agt.entrenar( alpha, gamma, epsilon, episodios, recompensa_media, n_episodios_media)
        self.thread_pool.start(self.segundo_plano)

        if not self.agt.playing:
            self.togglePlay()

