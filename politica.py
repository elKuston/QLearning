from abc import ABC, abstractmethod
import numpy as np
import random


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
    def __init__(self, epsilon, decaimiento_epsilon=1, semilla_random=0):
        """

        :param epsilon: La probabilidad de exploración aleatoria
        :param decaimiento_epsilon: El factor con el que se decrementa la variable epsilon Deberá estar en [0,1). 1 significa que epsilon es constante.
        :param semilla_random: La semilla para la generación de números aleatorios
        """
        super().__init__(epsilon, decaimiento_epsilon, semilla_random)

    def variar_parametro(self):
        """
        El parámetro epsilon disminuye exponencialmente (es decir, encada invocación, epsilon se multiplica por decaimiento_epsilon) sii anteriormente se ha invocado habilitar_variacion()
        """
        if self.variacion_habilitada:
            self.parametro *= self.variacion_parametro  # Epsilon decae exponencialmente

    def seleccionar_accion(self, agente):
        """
        Con una probabilidad epsilon selecciona una acción aleatoria de todas las posibles, y con probabilidad (1-epsilon) selecciona la que proporciona mejor recompensa estimada según Q
        :param agente: El agente que se está entrenando
        :return: La acción seleccionada
        """
        epsilon = self.parametro
        if random.uniform(0, 1) < epsilon: #Tomamos una acción aleatoria con probabilidad epsilon
            accion = agente.entorno.action_space.sample()
        else: #Con probabilidad (1-epsilon) elegimos la mejor acción según la matriz Q
            accion = np.argmax(agente.Q[agente.estado]) # argmax nos devuelve el índice del mayor elemento del array
        return accion


class SoftMax(Politica):
    def __init__(self, t, decremento_t=0, semilla_random=0):
        """
        :param t: La temperatura. Valores altos de t harán que todas las acciones tengan probabilidades similares de ser seleccionadas, mientras que valores próximos al 0 harán que la acción con mayor recompensa estimada sea la que tenga la mayor probabilidad de ser seleccionada
        :param decremento_t: La tasa de decremento de la temperatura. 0 significa que la temperatura es constante
        :param semilla_random: La semilla para el generador de números aleatorios
        """
        super().__init__(t, decremento_t, semilla_random)

    def variar_parametro(self):
        """
        Decrementa linealmente el parámetro T según decremento_t (es decir, en cada invocación se restará decremento_t a t) sii anteriormente se ha invocado habilitar_variación()

        """
        if self.variacion_habilitada:
            self.parametro -= self.variacion_parametro  # T disminuye linealmente

    def seleccionar_accion(self, agente):
        """
        Aplica la función softmax y elige una acción aleatoriamente, donde las acciones con mayor recompensa estimada tienen más probabilidad de ser elegidas (la magnitud de esto variará según el parámetro T)
        :param agente: El agente que se está entrenando
        :return: La acción seleccionada
        """
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

