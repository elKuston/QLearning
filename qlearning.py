import numpy as np

ACCION_IZQUIERDA = 0
ACCION_ABAJO = 1
ACCION_DERECHA = 2
ACCION_ARRIBA = 3


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

callback_ejecucion_inicio_paso = vacio  # Lo primero que se ejcuta al inciarse el paso de ejecución
callback_ejecucion_fin_paso = vacio  # Lo último que se ejecuta en el paso de ejecución
callback_ejecucion_inicio_ejecucion = vacio  # Lo primero que se ejecuta al llamar a la función ejecutar
callback_ejecucion_fin_ejecucion = vacio  # Lo último que se ejcuta al finalizar el entrenamiento


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
    agente.print_log("Problema completado en {} pasos; recompensa obtenida:{}".format(pasos, recompensa_total))
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

    callback_entrenamiento_inicio_entrenamiento()

    for episodio in range(episodios): #Repetir el problema tantas veces como episodios
        callback_enternamiento_inicio_episodio()
        agente.estado = agente.entorno.reset()#Reiniciamos el entorno en cada episodio
        es_final = False
        pasos = 0 #Contador de los pasos que da el agente
        recompensa_total = 0
        if episodio%1000 == 0:
            agente.print_log('Entrenando... (episodio: {})'.format(episodio))
        while not es_final: #Mientras no lleguemos a un estado final
            callback_entrenamiento_inicio_paso()
            accion = politica.seleccionar_accion()

            estado_siguiente, recompensa, es_final, info = agente.entorno.step(accion)  # Calcular el siguiente estado
            if modificar_recompensa:
                if not es_final:
                    recompensa = -0.0001  # Dar pasos tiene un coste (buscamos el camino mínimo)
                elif recompensa == 0:  # Estado final con recompensa 0 -> agujero
                    recompensa = -1  # Castigamos caerse al agujero
                    callback_entrenamiento_fracaso()
                else:  # Final y con recompensa -> estado objetivo
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
        ultimas_recompensas[episodio % n_episodios_media] = recompensa_total
        media = np.mean(ultimas_recompensas)
        if media >= recompensa_media:
            agente.print_log("El problema ha sido resuelto en {} episodios".format(episodio))
            agente.print_log("recompensa media obtenida últimos {} episodios: {}".format(n_episodios_media, media))
            break
        #print(agente.Q)
        if episodio % n_episodios_media == 0:
            agente.print_log("recompensa media obtenida últimos {} episodios: {}".format(n_episodios_media, media))
        callback_enternamiento_fin_episodio()
    # entorno.close()#Cerrar el entorno tras el entrenamiento
    # return Q
    callback_entrenamiento_fin_entrenamiento()
