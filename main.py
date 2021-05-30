from PyQt5 import QtWidgets, uic
import sys
from entornoWidget import EntornoWidget
import qlearning
import numpy as np
from Agente import Agente
import gym
from ventanas import VentanaPrincipal
from Controlador import Controlador
from politica import *

alpha = 0.1  # Tasa de aprendizaje
gamma = 1  # Determina cuánta importancia tienen las recompensas de los nuevos estados
epsilon = 0.5  # La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)

episodios = 50000  # Las "rondas" de entrenamiento
recompensa_media = 0.78  # Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
n_episodios_media = 100


def main():
    # Sirve para que se muestre mi icono en vez de el de python en la taskbar
    import ctypes
    myappid = u'CaponeraRomolo.TFG.QLearning.final'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    # miedito me da lo que pueda hacer esto honestly

    c = Controlador()
    c.registrar_algoritmo(SoftMax)
    c.registrar_algoritmo(UpperConfidenceBound)
    c.start()


if __name__ == '__main__':
    main()
