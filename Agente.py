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
        self.__played = True

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

    def entrenar(self, alpha, gamma, episodios, recompensa_media, n_episodios_media, politica):
        qlearning.callback_entrenamiento_fin_paso = self.controlador.actualizarVista
        qlearning.callback_entrenamiento_inicio_paso = self.esperar
        #qlearning.callback_entrenamiento_inicio_paso = self.esperar_play
        qlearning.entrenar(alpha, gamma, episodios, recompensa_media, n_episodios_media, self, politica)

    def esperar(self):
        time.sleep(0.01)
        self.esperar_play()

    def esperar_play(self):
        while not self.__played:
            time.sleep(0.01) # TODO esto es una basura de espera activa pero poco a poco, ya lo cambiaremos - Edit: parece que no hay muchas otras manera de hacerlo :/ porque parece que habria que crear un thread.Event para cada evento al que quiero que reaccione el programa y xd eso son muchos eventos cmo para pasar tantos parametros

    def toggle_play(self):
        self.__played = not self.__played
        if self.__played:
            text = "Pause"
        else:
            text = "Play"
        self.controlador.vista.playButton.setText(text)

from Controlador import Controlador
