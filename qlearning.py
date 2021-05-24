import numpy as np

ACCION_IZQUIERDA = 0
ACCION_ABAJO = 1
ACCION_DERECHA = 2
ACCION_ARRIBA = 3


def vacio(*args, **kwargs):
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
callback_entrenamiento_nueva_media = vacio

callback_ejecucion_inicio_paso = vacio  # Lo primero que se ejcuta al inciarse el paso de ejecución
callback_ejecucion_fin_paso = vacio  # Lo último que se ejecuta en el paso de ejecución
callback_ejecucion_inicio_ejecucion = vacio  # Lo primero que se ejecuta al llamar a la función ejecutar
callback_ejecucion_fin_ejecucion = vacio  # Lo último que se ejcuta al finalizar el entrenamiento


funcion_print = vacio


class QLearningBundle:
    def __init__(self, n_episodio, recompensa_media, historial_recompensa):
        self.n_episodio = n_episodio
        self.recompensa_media = recompensa_media
        self.historial_recompensa = historial_recompensa

    def __str__(self):
        return 'QLearning Bundle: n episodio: '+self.n_episodio\
               + '\nrecompensa media: '+self.recompensa_media \
               + '\nhistorial recompensa: '+self.historial_recompensa



def ejecutar(agente):
    agente.entorno._max_episode_steps = 9999999999999
    fin = False
    agente.estado = agente.entorno.reset()
    pasos = 0
    callback_ejecucion_inicio_ejecucion()
    recompensa_total = 0
    while not fin:
        callback_ejecucion_inicio_paso()
        #agente.entorno.render()
        accion = np.argmax(agente.Q[agente.estado])
        agente.estado, recompensa, fin, info = agente.entorno.step(accion)
        recompensa_total += recompensa
        pasos += 1
        callback_ejecucion_fin_paso()
    #entorno.render()
    funcion_print("Problema completado en {} pasos; recompensa obtenida:{}".format(pasos, recompensa_total))
    callback_ejecucion_fin_ejecucion()
    return recompensa


def reset(agente):
    agente.politica.inicializar_q()




def entrenar(alpha, gamma, episodios, recompensa_media, n_episodios_media, agente, modificar_recompensa=True):
    """Entrena el agente utilizando Q-Learning y devuelve la matriz Q obtenida


    :param alpha: Tasa de aprendizaje
    :param gamma: Determina cuánta importancia tienen las recompensas de los nuevos self.estados
    :param recompensa_media: La recompensa media para la que se considera que el problema está resuelto
    :param n_episodios_media: El número de episodios sobre el que se calcula la recompensa media (p. ej. los últimos 20 episodios)
    :param agente: el agente
    """

    politica = agente.politica
    #reset(agente)  TODO una cosita que he comentado porque no estoy seguro de si quitarla rompe todo el programa jeje

    ultimas_recompensas = np.zeros(n_episodios_media) #Lista que contiene las recompensas de los últimos n_episodios_media episodios

    bundle = QLearningBundle(0, 0, ultimas_recompensas)

    callback_entrenamiento_inicio_entrenamiento(bundle=bundle)

    for episodio in range(episodios): #Repetir el problema tantas veces como episodios
        bundle.n_episodio = episodio
        callback_enternamiento_inicio_episodio(bundle=bundle)
        agente.estado = agente.entorno.reset()#Reiniciamos el entorno en cada episodio
        es_final = False
        pasos = 0 #Contador de los pasos que da el agente
        recompensa_total = 0
        if episodio%1000 == 0:
            funcion_print('Entrenando... (episodio: {})'.format(episodio))
        while not es_final: #Mientras no lleguemos a un estado final
            callback_entrenamiento_inicio_paso(bundle=bundle)
            accion = politica.seleccionar_accion()

            estado_siguiente, recompensa, es_final, info = agente.entorno.step(accion)
            # TODO nuevo cambio: se calcula la media SIN modificar la recompensa
            recompensa_total += recompensa  # <-- todo joooooder cómo se nota xd
            if modificar_recompensa:
                if not es_final:
                    recompensa = -0.0001  # Dar pasos tiene un coste (buscamos el camino mínimo)
                elif recompensa == 0:  # Estado final con recompensa 0 -> agujero
                    recompensa = -1  # Castigamos caerse al agujero
                    callback_entrenamiento_fracaso(bundle=bundle)
                else:  # Final y con recompensa -> estado objetivo
                    politica.habilitar_variacion()
                    callback_entrenamiento_exito(bundle=bundle)
            callback_entrenamiento_recompensa(bundle=bundle)
            politica.actualizar_q(accion, estado_siguiente, recompensa, alpha, gamma)

            agente.estado = estado_siguiente
            pasos += 1
            # controlador.actualizarVista()
            callback_entrenamiento_fin_paso(bundle=bundle)
        politica.variar_parametro()
        ultimas_recompensas[episodio % n_episodios_media] = recompensa_total
        bundle.historial_recompensa = ultimas_recompensas
        media = np.mean(ultimas_recompensas)
        bundle.recompensa_media = media
        if media >= recompensa_media:
            funcion_print("El problema ha sido resuelto en {} episodios".format(episodio))
            funcion_print("recompensa media obtenida últimos {} episodios: {}".format(n_episodios_media, media))
            break
        #print(agente.Q)
        if episodio % n_episodios_media == 0:
            funcion_print("recompensa media obtenida últimos {} episodios: {}".format(n_episodios_media, media))
        if episodio % 10 ==0:
            callback_entrenamiento_nueva_media(bundle=bundle)
        callback_enternamiento_fin_episodio(bundle=bundle)
    # entorno.close()#Cerrar el entorno tras el entrenamiento
    # return Q
    callback_entrenamiento_fin_entrenamiento(bundle=bundle)
