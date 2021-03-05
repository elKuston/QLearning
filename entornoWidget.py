from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import numpy as np
import gym
import math
import qlearning

TAMANO_BLOQUE = 150
ESPACIO_ENTRE_BLOQUES = 2
LADO_CABEZA_FLECHA = 50  # El tamaño (en píxeles) del lado del triágulo que forma la punta de las flechas

COLOR_FLECHAS = QtGui.QColor(0, 0, 0)
COLOR_FLECHAS_NEGATIVAS = QtGui.QColor(255, 0, 0)
LONGITUD_FLECHAS = TAMANO_BLOQUE/3*0.8
GROSOR_FLECHA = 2

RADIO_AGENTE = 50


def obtener_mapa(entorno: gym.Env):
    """"
    Toma el entorno FrozenLake y lo convierte en una matriz de letras, siguiendo la misma representación que en el metodo render() del entorno: F-> casilla helada; H-> agujero;S-> Posicion inicial; G-> Posicion objetivo
    """
    mapa_str = entorno.render(mode='ansi')
    mapa = [[x for x in j if (x.isalpha() and x.isupper())] for j in mapa_str.split("\n") if len(j) > 0]
    return mapa


class EntornoWidget(QtWidgets.QWidget):

    def configurar(self, tamano, agente):
        self.tamano = tamano
        self.agente = agente
        self.mapa = obtener_mapa(agente.entorno)
        self.setFixedSize(TAMANO_BLOQUE*tamano+ESPACIO_ENTRE_BLOQUES*(tamano-1), TAMANO_BLOQUE*tamano+ESPACIO_ENTRE_BLOQUES*(tamano-1))

    def __init__(self, tamano = 0, agente=None):
        super().__init__()
        print("eoeeoooooo")
        if agente is not None and tamano != 0:
            self.configurar(tamano, agente)

    def paintEvent(self, e: QtGui.QPaintEvent) -> None:
        if self.agente is not None:
            painter = QtGui.QPainter(self)
            brush = QtGui.QBrush()
            brush.setColor(QtGui.QColor(120, 120, 120))
            brush.setStyle(Qt.SolidPattern)
            fondo = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
            painter.fillRect(fondo, brush)
            brush.setColor(QtGui.QColor(255, 255, 255))
            self.__dibujar_cuadricula(painter, brush)
            self.__dibujar_agente(painter)

    def __dibujar_cuadricula(self, painter, brush):
        font = painter.font()
        font.setFamily('Times')
        font.setBold(True)
        font.setPointSize(8)
        painter.setFont(font)

        for y in range(self.tamano):
            for x in range(self.tamano):
                self.__dibujar_casilla(x, y, painter, brush)

    def __dibujar_agente(self, painter):
        if self.agente.estado is not None:
            x, y = self.agente.estado%self.tamano, math.floor(self.agente.estado/self.tamano)
            x_pix = x*(TAMANO_BLOQUE + ESPACIO_ENTRE_BLOQUES)+TAMANO_BLOQUE/2 - RADIO_AGENTE/2
            y_pix = y*(TAMANO_BLOQUE + ESPACIO_ENTRE_BLOQUES)+TAMANO_BLOQUE/2 - RADIO_AGENTE/2
            painter.drawEllipse(x_pix, y_pix, RADIO_AGENTE, RADIO_AGENTE)

    def __dibujar_casilla(self, col, fil, painter, brush):
        x_ini = col*(TAMANO_BLOQUE + ESPACIO_ENTRE_BLOQUES)
        y_ini = fil*(TAMANO_BLOQUE + ESPACIO_ENTRE_BLOQUES)
        bloque = QtCore.QRect(x_ini,
                              y_ini,
                              TAMANO_BLOQUE,
                              TAMANO_BLOQUE)
        painter.fillRect(bloque, brush)
        pen = painter.pen()
        pen.setColor(QtGui.QColor(0, 0, 0))
        painter.setPen(pen)

        valor_q = np.max(self.agente.Q[fil*self.tamano+col])
        painter.drawText(x_ini, y_ini, TAMANO_BLOQUE, TAMANO_BLOQUE/3, Qt.AlignCenter, '{}\n{}'.format(
                         str(round(valor_q, 2)),
                         self.mapa[fil][col]))
        origen_flechas_x = x_ini+TAMANO_BLOQUE/2
        origen_flechas_y = y_ini+TAMANO_BLOQUE*2/3
        self.__dibujar4flechas(origen_flechas_x, origen_flechas_y, self.agente.Q[fil*self.tamano+col], painter)

    def __dibujar4flechas(self, x_origen, y_origen, q_estado, painter):
        for c in "UDLR":
            self.dibujar_flecha_direccion(x_origen, y_origen, q_estado, painter, c)

    def dibujar_flecha_direccion(self, x_origen, y_origen, q_estado, painter, direccion):
        incr_x = 0
        incr_y = 0
        color = COLOR_FLECHAS
        max_abs = np.max(np.abs(q_estado))
        max_index = np.argmax(q_estado)
        if max_abs == 0:
            max_abs = 1

        #switch direcciones
        #Ahora mismo dibuja en negro las flechas mayores que 0 o, si todas son negativas, la que tenga mayor valor, y el resto en rojo (las negativas)
        if direccion.upper() == 'U':#Arriba
            valor_q = q_estado[qlearning.ACCION_ARRIBA]
            incr_y = -LONGITUD_FLECHAS*abs(valor_q)/max_abs
        elif direccion.upper() == 'D':#Abajo
            valor_q = q_estado[qlearning.ACCION_ABAJO]
            incr_y = LONGITUD_FLECHAS*abs(valor_q)/max_abs
        elif direccion.upper() == 'L':#izquierda
            valor_q = q_estado[qlearning.ACCION_IZQUIERDA]
            incr_x = -LONGITUD_FLECHAS*abs(valor_q)/max_abs
        elif direccion.upper() == 'R':#Derecha
            valor_q = q_estado[qlearning.ACCION_DERECHA]
            incr_x = LONGITUD_FLECHAS*abs(valor_q)/max_abs
        else:
            raise ValueError('Direccion {} no reconocida'.format(direccion))

        if valor_q < 0:  # and max_index != qlearning.ACCION_DERECHA:
            color = COLOR_FLECHAS_NEGATIVAS

        self.__dibujar_flecha(x_origen, y_origen, x_origen+incr_x, y_origen+incr_y, painter, color)

    def __dibujar_flecha(self, x_origen, y_origen, x_destino, y_destino, painter, color=COLOR_FLECHAS):
        pen = painter.pen()
        pen.setColor(color)
        pen.setWidth(GROSOR_FLECHA)
        painter.setPen(pen)
        modulo = math.sqrt((x_destino-x_origen)**2+(y_destino-y_origen)**2)
        if modulo > 0:
            vector_unitario = np.array([x_destino-x_origen, y_destino-y_origen]) / modulo
            mod_altura = 0.3*modulo  # math.sqrt(0.75*LADO_CABEZA_FLECHA)  # Cuánto mide la altura del triángulo
            vector_altura = vector_unitario*mod_altura  # El vector de la altura
            v_perpendicular = np.array([vector_altura[1], -vector_altura[0]])  # Calcular un vector perpendicular a la altura (para la base)
            p_intersec_base = np.array([x_destino, y_destino]) - vector_altura
            p_base_1 = p_intersec_base+v_perpendicular*0.6
            p_base_2 = p_intersec_base-v_perpendicular*0.6

            fin_linea = p_intersec_base  # El punto en el que termina la línea de la flecha y empieza la cabeza (hay que dejar de dinujarla aqui para que no atraviese el triangulo de la flecha y quede feo)
            painter.drawLine(x_origen, y_origen, fin_linea[0], fin_linea[1])
            punta_flecha = QtGui.QPainterPath(QtCore.QPoint(x_destino, y_destino))
            punta_flecha.lineTo(p_base_2[0], p_base_2[1])
            punta_flecha.lineTo(p_base_1[0], p_base_1[1])
            punta_flecha.lineTo(x_destino, y_destino)
            painter.fillPath(punta_flecha, QtGui.QBrush(color))

