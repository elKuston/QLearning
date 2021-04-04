import random
import sys

import gym
import numpy as np

ACCION_IZQUIERDA = 0
ACCION_ABAJO = 1
ACCION_DERECHA = 2
ACCION_ARRIBA = 3

nombre_entorno = 'FrozenLake8x8-v0'


def vacio():
    pass


callback_entrenamiento_inicio_paso = vacio  # Lo primero que se ejcuta al inciarse el paso de entrenamiento
callback_entrenamiento_fin_paso = vacio  # Lo último que se ejecuta en el paso de entrenamiento
callback_entrenamiento_recompensa = vacio  # Se ejecuta al recibir una recompensa (aunque esta sea 0)
callback_entrenamiento_exito = vacio  # Se ejecuta al llegar al estado objetivo
callback_entrenamiento_fracaso = vacio  # Se ejecuta al llegar a un estado final no objetivo
callback_enternamiento_inicio_episodio = vacio  # Lo primero que se ejecuta al empezar un nuevo episodio
callback_enternamiento_fin_episodio = vacio  # Lo último que se ejecuta al finalizar un episodio
callback_entrenamiento_inicio_entrenamiento = vacio  # Lo primero que se ejecuta al llamar a la función entrenamiento
callback_entrenamiento_fin_entrenamiento = vacio  # Lo último que se ejcuta al finalizar el entrenamiento


def main():
    alpha = 0.618 #Tasa de aprendizaje
    gamma = 0.99 #Determina cuánta importancia tienen las recompensas de los nuevos estados 
    epsilon = 0.2 #La probabilidad  de tomar una acción aleatoria (en lugar de la que la política nos dice que es mejor)

    episodios = 10000 #Las "rondas" de entrenamiento
    recompensa_media = 0.78 #Según la documentación, se considera que este problema está resuelto si en los últimos 100 episodios se obtiene una recompensa media de al menos 0.78
    n_episodios_media = 100

    entrenar(alpha, gamma, epsilon, episodios, recompensa_media, n_episodios_media)
    entorno = gym.make(nombre_entorno)
    ejecutar(entorno, Q)
    entorno.close()


def ejecutar(entorno, Q):
    entorno._max_episode_steps = 9999999999999
    fin = False
    estado = entorno.reset()
    pasos = 0
    while not fin:
        entorno.render()
        accion = np.argmax(Q[estado])
        estado, recompensa, fin, info = entorno.step(accion)
        pasos+=1
    entorno.render()
    print("Problema completado en {} pasos".format(pasos))
    return recompensa


def reset(agente, episodios=200):
    if agente.entorno is None:
        agente.entorno = gym.make(nombre_entorno)
        agente.entorno._max_episode_steps = episodios+1
    if agente.Q is None:
        print("NOne")
        agente.politica.inicializar_q()


def entrenar(alpha, gamma, episodios, recompensa_media, n_episodios_media, agente, modificar_recompensa=True):
    """Entrena el agente utilizando Q-Learning y devuelve la matriz Q obtenida


    :param alpha: Tasa de aprendizaje
    :param gamma: Determina cuánta importancia tienen las recompensas de los nuevos self.estados
    :param recompensa_media: La recompensa media para la que se considera que el problema está resuelto
    :param n_episodios_media: El número de episodios sobre el que se calcula la recompensa media (p. ej. los últimos 20 episodios)
    :param agente: el agente
    """
    callback_entrenamiento_inicio_entrenamiento()
    #if agente.entorno is None:
     #   agente.entorno = gym.make(nombre_entorno)
    #agente.entorno._max_episode_steps = episodios+1
    #if agente.Q is None:
     #   print("NOne")
      #  politica.inicializar_q()
    politica = agente.politica
    reset(agente, episodios)

    ultimas_recompensas = np.zeros(n_episodios_media) #Lista que contiene las recompensas de los últimos n_episodios_media episodios

    for episodio in range(episodios): #Repetir el problema tantas veces como episodios
        callback_enternamiento_inicio_episodio()
        agente.estado = agente.entorno.reset()#Reiniciamos el entorno en cada episodio
        es_final = False
        pasos = 0 #Contador de los pasos que da el agente
        recompensa_total = 0
        if episodio%1000 == 0:
            print("Entrenando... (episodio: {})".format(episodio))
        while not es_final: #Mientras no lleguemos a un estado final
            callback_entrenamiento_inicio_paso()
            accion = politica.seleccionar_accion()

            estado_siguiente, recompensa, es_final, info = agente.entorno.step(accion)  # Calcular el siguiente estado
            if modificar_recompensa:
                if not es_final:
                    recompensa = -0.0001#Dar pasos tiene un coste (buscamos el camino mínimo)
                elif recompensa == 0: #Estado final con recompensa 0 -> agujero
                    recompensa = -1#Castigamos caerse al agujero
                    callback_entrenamiento_fracaso()
                else:  #Final y con recompensa -> estado objetivo
                    politica.habilitar_variacion()
                    callback_entrenamiento_exito()
            callback_entrenamiento_recompensa()
            recompensa_total += recompensa
            politica.actualizar_q(accion, estado_siguiente, recompensa, alpha, gamma)

            agente.estado = estado_siguiente
            pasos += 1
            # controlador.actualizarVista()
            callback_entrenamiento_fin_paso()
        politica.variar_parametro()
        ultimas_recompensas[episodio%n_episodios_media] = recompensa_total
        media = np.mean(ultimas_recompensas)
        if media >= recompensa_media:
            print("El problema ha sido resuelto en {} episodios".format(episodio))
            print("recompensa media obtenida últimos {} episodios".format(n_episodios_media), media)
            break
        #print(agente.Q)
        if episodio % n_episodios_media == 0:
            print("recompensa media obtenida últimos {} episodios".format(n_episodios_media), media)
        callback_enternamiento_fin_episodio()
    # entorno.close()#Cerrar el entorno tras el entrenamiento
    # return Q
    callback_entrenamiento_fin_entrenamiento()


if __name__ == '__main__':
    main()