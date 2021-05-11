from abc import ABC, abstractmethod
import numpy as np
import random
import math


class Politica(ABC):
    def __init__(self, agente, parametro, variacion_parametro, semilla_random=0):
        self.agente = agente
        self.parametro = parametro
        self.semilla = semilla_random
        self.variacion_parametro = variacion_parametro
        self.variacion_habilitada = False

    def inicializar_q(self, **kwargs):
        """
        Inicializa la matriz Q del agente con valor
        :param valor: El valor con el que se inicializa la matriz
        """
        valor = kwargs.get('valor', 0)
        self.agente.Q = np.full([self.agente.entorno.observation_space.n, self.agente.entorno.action_space.n], valor, dtype='float64')

    def actualizar_q(self, accion, estado_siguiente, recompensa, alpha, gamma):
        """
        Actualiza el valor de la matriz Q tras el cambio de estado
        :param accion: La acción realizada por el agente
        :param estado_siguiente: El estado al que ha llegado el agente tras realizar la acción
        :param recompensa: La recompensa obtenida al realizar la acción
        :param alpha: Tasa de aprendizaje
        :param gamma: Tasa de descuento
        """
        max_siguiente = np.max(self.agente.Q[estado_siguiente])  # El mejor valor que podríamos obtener yendo al estado estado_siguiente
        self.agente.Q[self.agente.estado, accion] = (1-alpha) * self.agente.Q[self.agente.estado, accion] + alpha*(recompensa + gamma*max_siguiente)  # aplicamos la formula del Q-Learning

    def habilitar_variacion(self, habilitada=True):
        """
        Habilita o deshabilita la variación del parámetro con el tiempo. Si está deshabilitada, variar_parametro() no tendrá efecto
        """
        self.variacion_habilitada = habilitada

    @abstractmethod
    def variar_parametro(self):
        """
        Varia el parámetro de la variante
        """

    @abstractmethod
    def seleccionar_accion(self):
        """
        Selecciona una acción
        """



class EpsilonGreedy(Politica):
    def __init__(self, agente, epsilon, decaimiento_epsilon=1, semilla_random=0):
        """

        :param epsilon: La probabilidad de exploración aleatoria
        :param decaimiento_epsilon: El factor con el que se decrementa la variable epsilon Deberá estar en [0,1). 1 significa que epsilon es constante.
        :param semilla_random: La semilla para la generación de números aleatorios
        """
        super().__init__(agente, epsilon, decaimiento_epsilon, semilla_random)

    def variar_parametro(self):
        """
        El parámetro epsilon disminuye exponencialmente (es decir, encada invocación, epsilon se multiplica por decaimiento_epsilon) sii anteriormente se ha invocado habilitar_variacion()
        """
        if self.variacion_habilitada:
            self.parametro *= self.variacion_parametro  # Epsilon decae exponencialmente

    def seleccionar_accion(self):
        """
        Con una probabilidad epsilon selecciona una acción aleatoria de todas las posibles, y con probabilidad (1-epsilon) selecciona la que proporciona mejor recompensa estimada según Q
        :param agente: El agente que se está entrenando
        :return: La acción seleccionada
        """
        epsilon = self.parametro
        if random.uniform(0, 1) < epsilon: #Tomamos una acción aleatoria con probabilidad epsilon
            accion = self.agente.entorno.action_space.sample()
        else: #Con probabilidad (1-epsilon) elegimos la mejor acción según la matriz Q
            accion = np.argmax(self.agente.Q[self.agente.estado]) # argmax nos devuelve el índice del mayor elemento del array
        return accion


class SoftMax(Politica):
    def __init__(self, agente, t, decremento_t=0, semilla_random=0):
        """
        :param t: La temperatura. Valores altos de t harán que todas las acciones tengan probabilidades similares de ser seleccionadas, mientras que valores próximos al 0 harán que la acción con mayor recompensa estimada sea la que tenga la mayor probabilidad de ser seleccionada
        :param decremento_t: La tasa de decremento de la temperatura. 0 significa que la temperatura es constante
        :param semilla_random: La semilla para el generador de números aleatorios
        """
        super().__init__(agente, t, decremento_t, semilla_random)

    def variar_parametro(self):
        """
        Decrementa linealmente el parámetro T según decremento_t (es decir, en cada invocación se restará decremento_t a t) sii anteriormente se ha invocado habilitar_variación()

        """
        if self.variacion_habilitada:
            #self.parametro -= self.variacion_parametro  # T disminuye linealmente
            self.parametro *= self.variacion_parametro

    def seleccionar_accion(self):
        """
        Aplica la función softmax y elige una acción aleatoriamente, donde las acciones con mayor recompensa estimada tienen más probabilidad de ser elegidas (la magnitud de esto variará según el parámetro T)
        :param agente: El agente que se está entrenando
        :return: La acción seleccionada
        """
        probabilidades = self.__softmax(self.agente.Q[self.agente.estado], self.parametro)
        rand = random.uniform(0, 1)
        # Vamos a elegir la acción que se corresponde con esa probabilidad. Para ello cogemos la primera accion cuya probabilidad acumulada supera al número aleatorio
        i = 0
        prob = probabilidades[i]
        while rand > prob and i < len(probabilidades):
            i += 1
            prob += probabilidades[i]
        #print('rand', rand, 'cumsum', np.cumsum(probabilidades), 'seleccionado', i)
        return i

    def __softmax(self, q_estado, t):
        probabilidades = np.exp(q_estado/t)  #Con temp
        #probabilidades = np.exp(q_estado)  #Sin temp
        suma = np.sum(probabilidades)
        softmax = probabilidades/suma
        return softmax

    def __softmax_notemp(self, q_estado):
        probabilidades = np.exp(q_estado)  #Sin temp
        suma = np.sum(probabilidades)
        softmax = probabilidades/suma
        return softmax


class UpperConfidenceBound(Politica):
    def __init__(self, agente, H, T, semilla_random=0):
        """

        :param agente: El agente que se desea entrenar
        :param H: Número de pasos por episodio
        :param T: Número de pasos totales (de todos los episodios)
        :param semilla_random: Semilla para la generación de números aleatorios (En este algoritmo no se utilizan, pero al heredar de Política es necesario mantener el parámetro)
        """
        super().__init__(agente, H, T, semilla_random)
        self.H = H
        self.T = T
        self.N = np.zeros([agente.entorno.observation_space.n, agente.entorno.action_space.n])
        self.V = np.full(agente.entorno.observation_space.n, 0)

    def inicializar_q(self):
        super().inicializar_q(valor=self.H)

    def actualizar_q(self, accion, estado_siguiente, recompensa, alpha_no_se_usa, gamma):
        self.N[self.agente.estado, accion] += 1
        t = self.N[self.agente.estado, accion]
        alpha = (self.H + 1)/(self.H + t)
        c = 1  # TODO no tengo nidea de qué es c pero asumo que será alguna constante y aquí dejo esto puesto pa implementar el algoritmo mientras lo averiguo xd
        p = 1  # TODO otra cosa que no tengo npi xd
        lg = math.log10(self.agente.entorno.observation_space.n*self.agente.entorno.action_space.n*self.T/p)
        b_t = c * math.sqrt(self.H**3*lg/t)
        self.agente.Q[self.agente.estado, accion] = (1-alpha)*self.agente.Q[self.agente.estado, accion] + alpha * (recompensa + self.V[estado_siguiente] + b_t)
        self.V[self.agente.estado] = min(self.H, np.max(self.agente.Q[self.agente.estado]))  # El mínimo entre H y el máximo valor del estado

    def seleccionar_accion(self):
        # Elegimos la mejor acción según la matriz Q
        accion = np.argmax(self.agente.Q[self.agente.estado])  # argmax nos devuelve el índice del mayor elemento del array
        return accion

    def variar_parametro(self):
        pass