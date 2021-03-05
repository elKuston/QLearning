from abc import ABC, abstractmethod
import numpy as np
import random
import math
import sys


class Politica(ABC):
    @abstractmethod
    def seleccionar_accion(self, agente, parametro):
        """
        Selecciona una acción

        :parameter agente: El objeto Agente que se está entrenando
        """


class EpsilonGreedy(Politica):
    def __init__(self, semilla_random=0):
        random.seed(semilla_random)
    def seleccionar_accion(self, agente, epsilon):
        if random.uniform(0, 1) < epsilon: #Tomamos una acción aleatoria con probabilidad epsilon
            accion = agente.entorno.action_space.sample()
        else: #Con probabilidad (1-epsilon) elegimos la mejor acción según la matriz Q
            accion = np.argmax(agente.Q[agente.estado]) # argmax nos devuelve el índice del mayor elemento del array
        return accion


class SoftMax(Politica):
    def seleccionar_accion(self, agente, parametro_variante):
        probabilidades = self.__softmax(agente.Q[agente.estado], sys.maxsize)
        rand = random.uniform(0, 1)
        # Vamos a elegir la acción que se corresponde con esa probabilidad. Para ello cogemos la primera accion cuya probabilidad acumulada supera al número aleatorio
        i = 0
        prob = probabilidades[i]
        while rand > prob and i < len(probabilidades):
            i += 1
            prob += probabilidades[i]
        return i

    def __softmax(self, q_estado, t):
        probabilidades = np.exp(q_estado/t)
        suma = np.sum(probabilidades)
        softmax = probabilidades/suma
        return softmax

