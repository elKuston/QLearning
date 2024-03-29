import time

from PyQt5.QtCore import QThread, pyqtSignal

import frozenLake
from Agente import Agente
import Controlador
import qlearning
import utils


class SignalBuffer:
    """Las hebras de entrenamiento y ejecución emiten muchísimas señales por segundo
    (para el refresco de la pantalla). De esta manera se reduce el número de señales a un
    máximo de 60 por segundo (la tasa de refresco más común en los monitores)"""
    def __init__(self, sig, frecuencia_max, n_args=0):
        self.sig = sig
        self.frecuencia_max = frecuencia_max
        self.ultima_emision = time.time()
        self.n_args = n_args
        self.param_buffer = [[] for i in range(n_args)]

    def emit(self, *params):
        """

        :param params:
        :return: Si la señal se ha emitido o no
        """
        emitted = False
        for index in range(self.n_args):
            self.param_buffer[index].append(params[index])

        t = time.time()
        if t - self.ultima_emision >= self.frecuencia_max:
            self.ultima_emision = t
            if self.n_args > 0:
                self.sig.emit(*self.param_buffer)
            else:
                self.sig.emit()
            emitted = True
            self.param_buffer = [[] for i in range(self.n_args)]

        return emitted

    def flush(self, **kwargs):
        self.sig.emit(*self.param_buffer)
        self.param_buffer = [[] for i in range(self.n_args)]


class ThreadEntrenamiento(QThread):
    sig_actualizar_vista = pyqtSignal()
    sig_print = pyqtSignal(str)
    sig_plot = pyqtSignal(list, list)  # x and y
    sig_fin_entrenamiento = pyqtSignal()

    def __init__(self, controlador: Controlador, agente, alpha, gamma, episodios, recompensa_media, n_episodios_media):
        super().__init__()
        self.controlador = controlador
        self.tiempo_espera = 10/1000  #10 ms TODO cambiar esto para que no se inicialice siempre en 10 (porque si no al cambiar de mapa se desincroniza con la slide bar)
        self.controlador.sig_cambiar_tiempo_espera.connect(self.cambiar_tiempo_espera)
        self.agente = agente
        self.alpha = alpha
        self.gamma = gamma
        self.episodios = episodios
        self.recompensa_media = recompensa_media
        self.n_episodios_media = n_episodios_media
        self.sig_buf = SignalBuffer(self.sig_actualizar_vista, 16/1000, 0)

        self.plot_buf = SignalBuffer(self.sig_plot, 16/1000, 2)  # TODO
        self.i = 0

    def run(self):
        qlearning.callback_entrenamiento_fin_entrenamiento = qlearning.vacio

        qlearning.callback_entrenamiento_inicio_entrenamiento = self.inicio
        qlearning.callback_entrenamiento_fin_paso = self.actualizar_vista
        qlearning.callback_entrenamiento_inicio_paso = self.esperar
        qlearning.callback_enternamiento_fin_episodio = self.anadir_plot
        qlearning.funcion_print = self.log
        qlearning.callback_entrenamiento_fin_entrenamiento = self.fin_entrenamiento
        qlearning.entrenar(self.alpha, self.gamma, self.episodios, self.recompensa_media,
                           self.n_episodios_media, self.agente, self.agente.politica)

    def actualizar_vista(self, **kwargs):
        self.sig_buf.emit()

    def anadir_plot(self, **kwargs):
        if 'bundle' in kwargs:
            bundle = kwargs.get("bundle")
            self.plot_buf.emit(bundle.n_episodio, bundle.recompensa_media)

    def log(self, message):
        self.sig_print.emit(message)

    def esperar(self, **kwargs):
        self.msleep(int(1000*self.tiempo_espera))

    def cambiar_tiempo_espera(self, nuevo_tiempo):
        self.tiempo_espera = nuevo_tiempo

    def print_policy(self):
        self.log("Iniciando entrenamiento...\n\tPolitica: "+str(self.agente.politica))

    def inicio(self, **kwargs):
        self.actualizar_vista()
        self.print_policy()

    def fin_entrenamiento(self, **kwargs):
        self.plot_buf.flush()
        self.sig_fin_entrenamiento.emit()


class ThreadEjecucion(QThread):

    sig_actualizar_vista = pyqtSignal()
    sig_print = pyqtSignal(str)

    def __init__(self, controlador: Controlador, agente):
        super().__init__()
        self.controlador = controlador
        self.controlador.sig_cambiar_tiempo_espera.connect(self.cambiar_tiempo_espera)
        self.agente = agente
        # 10 ms Placeholder: este valor no se utiliza porque al generar los hilos se emite sig_cambiar_tiempo_espera
        self.tiempo_espera = 10 / 1000

        self.sig_buf = SignalBuffer(self.sig_actualizar_vista, 16/1000, 0)

    def run(self):
        utils.reset_qlearning_callbacks()
        qlearning.callback_ejecucion_inicio_ejecucion = self.actualizar_vista
        qlearning.callback_ejecucion_fin_paso = self.actualizar_vista
        qlearning.callback_ejecucion_inicio_paso = self.esperar
        qlearning.funcion_print = self.log
        qlearning.ejecutar(self.agente)

    def log(self, message):
        self.sig_print.emit(message)

    def actualizar_vista(self):
        self.sig_buf.emit()

    def esperar(self):
        self.msleep(int(1000*self.tiempo_espera))

    def cambiar_tiempo_espera(self, nuevo_tiempo):
        self.tiempo_espera = nuevo_tiempo
        print(self.tiempo_espera, 'ms')


class ThreadBenchmark(QThread):
    sig_actualizar_benchmark = pyqtSignal(str, int)  # nombre del algoritmo y Número de episodios

    def __init__(self, entorno, controlador, politicas, episodios, ajustes_dict, recompensa_media=0.78, n_episodios_media=100):
        super().__init__()
        self.entorno = frozenLake.FrozenLake(entorno.nombre_mapa)
        self.controlador = controlador
        self.agente = Agente(entorno, controlador)
        self.politicas = politicas
        self.episodios = episodios
        self.ajustes = ajustes_dict
        self.n_ejecuciones = ajustes_dict[utils.AJUSTES_PARAM_N_EJECUCIONES]
        self.recompensa_media = recompensa_media
        self.n_episodios_media = n_episodios_media

    def run(self):
        print("Iniciando benchmark")

        qlearning.callback_entrenamiento_inicio_entrenamiento = qlearning.vacio
        qlearning.callback_entrenamiento_fin_paso = qlearning.vacio
        qlearning.callback_entrenamiento_inicio_paso = qlearning.vacio
        qlearning.callback_enternamiento_fin_episodio = qlearning.vacio
        qlearning.funcion_print = qlearning.vacio

        qlearning.callback_entrenamiento_fin_entrenamiento = self.fin_ejecucion
        for clase_politica in self.politicas:
            nombre = clase_politica.get_nombre()
            alpha = self.ajustes[nombre]['alpha']
            gamma = self.ajustes[nombre]['gamma']
            p1 = self.ajustes[nombre]['param1']
            p2 = self.ajustes[nombre]['param2']

            for e in range(self.n_ejecuciones):
                pol = clase_politica(self.agente, p1, p2)
                self.politica_actual = pol.get_nombre()
                self.agente.set_politica(pol)
                self.agente.reset()
                qlearning.entrenar(alpha, gamma, self.episodios, self.recompensa_media,
                                   self.n_episodios_media, self.agente, self.agente.politica)
                print('ejecucion',e,'completada')

    def fin_ejecucion(self, **kwargs):
        bundle = kwargs.get('bundle')
        n_pasos = bundle.n_episodio
        self.sig_actualizar_benchmark.emit(self.politica_actual, n_pasos)
