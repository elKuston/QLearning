from abc import ABC, abstractmethod
import numpy as np
import random

class Politica(ABC):

    @abstractmethod
    def seleccionar_accion(self, entorno, epsilon, Q):
        """
        :return Selecciona una acción siguiendo la politica seleccionada
        :parameter Q La matriz Q del agente
        :param entorno El entorno en el que se está seleccionando la accion
        """
