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

    def __init__(self, entorno: gym.Env, controlador):
        self.entorno = entorno
        self.estado = None
        self.controlador = controlador
        self.Q = np.zeros([entorno.observation_space.n, entorno.action_space.n])  # El agente contiene su matriz Q

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

    def entrenar(self, alpha, gamma, epsilon, episodios, recompensa_media, n_episodios_media):
        qlearning.callback_entrenamiento_fin_paso = self.controlador.actualizarVista
        qlearning.entrenar(alpha, gamma, epsilon, episodios, recompensa_media, n_episodios_media, self)





from Controlador import Controlador
