import time

import setuptools
from PyQt5.QtCore import QThread, pyqtSignal

import Controlador
import qlearning


class SignalBuffer:
    """Las hebras de entrenamiento y ejecución emiten muchísimas señales por segundo
    (para el refresco de la pantalla). De esta manera se reduce el número de señales a un
    máximo de 60 por segundo (la tasa de refresco más común en los monitores)"""
    def __init__(self, sig, frecuencia_max):
        self.sig = sig
        self.frecuencia_max = frecuencia_max
        self.ultima_emision = time.time()

    def emit(self, *params):
        t = time.time()
        if t - self.ultima_emision >= 16/1000:  # Solo emite señales cada 16ms (60hz)
            self.ultima_emision = t
            self.sig.emit(*params)


class ThreadEntrenamiento(QThread):
    sig_actualizar_vista = pyqtSignal()
    sig_print = pyqtSignal(str)

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
        self.sig_buf = SignalBuffer(self.sig_actualizar_vista, 16/1000)

    def run(self):
        qlearning.callback_entrenamiento_inicio_entrenamiento = self.inicio
        qlearning.callback_entrenamiento_fin_paso = self.actualizar_vista
        qlearning.callback_entrenamiento_inicio_paso = self.esperar
        qlearning.funcion_print = self.log
        qlearning.entrenar(self.alpha, self.gamma, self.episodios, self.recompensa_media,
                           self.n_episodios_media, self.agente, self.agente.politica)

    def actualizar_vista(self):
        self.sig_buf.emit()

    def log(self, message):
        self.sig_print.emit(message)

    def esperar(self):
        time.sleep(self.tiempo_espera)

    def cambiar_tiempo_espera(self, nuevo_tiempo):
        self.tiempo_espera = nuevo_tiempo

    def print_policy(self):
        self.log("Iniciando entrenamiento...\n\tPolitica: "+str(self.agente.politica))

    def inicio(self):
        self.actualizar_vista()
        self.print_policy()


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

        self.sig_buf = SignalBuffer(self.sig_actualizar_vista, 16/1000)

    def run(self):
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
        time.sleep(self.tiempo_espera)

    def cambiar_tiempo_espera(self, nuevo_tiempo):
        self.tiempo_espera = nuevo_tiempo


