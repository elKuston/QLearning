import numpy as np
import gym
import qlearning
import random
import sys
import time

from politica import Politica


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
        self.Q = np.zeros([self.entorno.observation_space.n, self.entorno.action_space.n])  # El agente contiene su matriz Q TODO esto no deberia ser necesario, se deberia inicializar desde la politica
        qlearning.reset(self, self.politica)  #TODO

    def set_politica(self, politica):
        self.politica = politica

    def __init__(self, entorno: gym.Env, controlador):
        self.entorno = entorno
        self.estado = None
        self.controlador = controlador
        self.Q = np.zeros([entorno.observation_space.n, entorno.action_space.n])  # El agente contiene su matriz Q
        self.playing = True
        self.tiempo_espera = 0.01
        self.politica = None  # Algo hay que poner para que no se queje de que está definido fuera del init

    def resolver(self):
        self.entorno._max_episode_steps = 9999999999999
        fin = False
        estado = self.entorno.reset()
        pasos = 0
        print("Resolviendo problema")
        while not fin:
            accion = np.argmax(self.Q[estado])
            estado, recompensa, fin, info = self.entorno.step(accion)
            pasos+=1
            self.controlador.actualizarVista()
            time.sleep(1)
        print("Problema completado en {} pasos".format(pasos))

    def entrenar(self, alpha, gamma, episodios, recompensa_media, n_episodios_media):
        qlearning.callback_entrenamiento_fin_paso = self.controlador.actualizarVista
        qlearning.callback_entrenamiento_inicio_paso = self.esperar
        #qlearning.callback_entrenamiento_inicio_paso = self.esperar_play
        print(self.Q)
        qlearning.entrenar(alpha, gamma, episodios, recompensa_media, n_episodios_media, self, self.politica)

    def esperar(self):
        if self.tiempo_espera >= 0.01:  # 10ms es lo mínimo que soporta (en windows) el time.sleep. Si nos piden menos, directamente no esperamos
            time.sleep(self.tiempo_espera)
        self.esperar_play()

    def esperar_play(self):
        while not self.playing:
            time.sleep(0.01)  # TODO esto es una basura de espera activa pero poco a poco, ya lo cambiaremos - Edit: parece que no hay muchas otras manera de hacerlo :/ porque parece que habria que crear un thread.Event para cada evento al que quiero que reaccione el programa y xd eso son muchos eventos cmo para pasar tantos parametros

    def toggle_play(self):
        self.playing = not self.playing

    def cambiar_tiempo_espera(self, tiempo_espera):
        self.tiempo_espera = tiempo_espera

from Controlador import Controlador
