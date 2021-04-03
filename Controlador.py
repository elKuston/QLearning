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
        app = QtWidgets.QApplication(sys.argv)
        entorno = gym.make(qlearning.nombre_entorno)
        self.agt = Agente(entorno, self)
        self.vista = VentanaPrincipal(8, self.agt)
        self.vista.playButton.clicked.connect(self.togglePlay)
        #self.vista = EntornoWidget(8, agt)
        self.vista.show()
        tp = QThreadPool()
        sp = SegundoPlano(self.agt.entrenar, alpha, gamma, episodios, recompensa_media, n_episodios_media, EpsilonGreedy(self.agt, epsilon, 0.9))
        # agt.entrenar( alpha, gamma, epsilon, episodios, recompensa_media, n_episodios_media)
        tp.start(sp)
        print("ENTRENAMIENTO FINALIZADO")
        # sp = SegundoPlano(agt.resolver)
        #tp.start(sp)
        sys.exit(app.exec_())

    def actualizarVista(self):
        self.vista.update()

    def paso(self):
        print("paso")

    def togglePlay(self):
        print("PLAY TOGGLED from Controlador")
        self.agt.toggle_play()