import numpy as np
import qlearning
import time
from frozenLake import FrozenLake


class Agente:
    def vacio(self):
        pass

    callback_entrenamiento_inicio_paso = vacio  # Lo primero que se ejcuta al inciarse el paso de entrenamiento
    callback_entrenamiento_fin_paso = vacio  # Lo último que se ejecuta en el paso de entrenamiento
    callback_entrenamiento_recompensa = vacio  # Se ejecuta al recibir una recompensa (aunque esta sea 0)
    callback_entrenamiento_exito = vacio  # Se ejecuta al llegar al estado objetivo
    callback_entrenamiento_fracaso = vacio  # Se ejecuta al llegar a un estado final no objetivo

    def reset(self):
        self.estado = None
        #self.entorno.reset()
        qlearning.reset(self)

    def set_politica(self, politica):
        self.politica = politica

    def __init__(self, entorno: FrozenLake, controlador):
        self.entorno = entorno
        self.estado = None
        self.controlador = controlador
        self.Q = np.zeros([entorno.observation_space.n, entorno.action_space.n])  # El agente contiene su matriz Q
        self.playing = False
        self.tiempo_espera = 0.01
        self.politica = None  # Algo hay que poner para que no se queje de que está definido fuera del init

        self.ultimo_refresco = time.time()

    @property
    def readonly_Q(self):  #TODO cambiar por una property Q protegida por mutex
        return np.copy(self.Q)

    def toggle_play(self):
        self.playing = not self.playing

    def cambiar_tiempo_espera(self, tiempo_espera):
        self.tiempo_espera = tiempo_espera

    def print_log(self, text):
        if self.controlador is not None:
            self.controlador.print_log(text)
        else:
            print("Error: Controlador is None")

from Controlador import Controlador
