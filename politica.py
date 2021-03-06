from abc import ABC, abstractmethod
import numpy as np
import random
import math
import sys


class Politica(ABC):
    def __init__(self, parametro, variacion_parametro, semilla_random=0):
        self.parametro = parametro
        self.semilla = semilla_random
        self.variacion_parametro = variacion_parametro
        self.variacion_habilitada = False

    def habilitar_variacion(self, habilitada=True):
        """
        Habilita o deshabilita la variación del parámetro con el tiempo. Si está deshabilitada, variar_parametro() no tendrá efecto
        :return:
        """
        self.variacion_habilitada = habilitada

    @abstractmethod
    def variar_parametro(self):
        """
        Varia el parámetro de la variante
        :return:
        """

    @abstractmethod
    def seleccionar_accion(self, agente):
        """
        Selecciona una acción

        :parameter agente: El objeto Agente que se está entrenando
        """


class EpsilonGreedy(Politica):
    def __init__(self, epsilon, decaimiento_epsilon, semilla_random=0):
        super().__init__(epsilon, decaimiento_epsilon, semilla_random)

    def variar_parametro(self):
        if self.variacion_habilitada:
            self.parametro *= self.variacion_parametro  # Epsilon decae exponencialmente

    def seleccionar_accion(self, agente):
        epsilon = self.parametro
        if random.uniform(0, 1) < epsilon: #Tomamos una acción aleatoria con probabilidad epsilon
            accion = agente.entorno.action_space.sample()
        else: #Con probabilidad (1-epsilon) elegimos la mejor acción según la matriz Q
            accion = np.argmax(agente.Q[agente.estado]) # argmax nos devuelve el índice del mayor elemento del array
        return accion


class SoftMax(Politica):
    def __init__(self, t, incremento_t, semilla_random=0):
        super().__init__(t, incremento_t, semilla_random)

    def variar_parametro(self):
        if self.variacion_habilitada:
            self.parametro -= self.variacion_parametro  # T disminuye linealmente

    def seleccionar_accion(self, agente):
        probabilidades = self.__softmax(agente.Q[agente.estado], self.parametro)
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

