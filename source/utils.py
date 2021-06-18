import random
import qlearning
import utils

FORMATO_FICHERO = '.pol'

NOMBRE_APP = 'QLearning'
NOMBRE_MODULO_SETTINGS = 'Benchmark'
AJUSTES_PARAM_N_EJECUCIONES = 'numero ejecuciones'
AJUSTES_PARAM_MODO_BENCHMARK = 'modo benchmark'
AJUSTES_BENCHMARK_MODO_BARRAS = 'Barras'
AJUSTES_BENCHMARK_MODO_CAJA = 'Cajas'

MODOS_BEMCHMARK = [AJUSTES_BENCHMARK_MODO_BARRAS, AJUSTES_BENCHMARK_MODO_CAJA]


def guardar_fichero(nombre_fichero, contenido):
    fichero = open(nombre_fichero, 'w')
    fichero.write(contenido)
    fichero.close()


def generar_matriz_exportable(Q):
    """Devuelve un string con el contenido de la matriz Q en el formato con el que se importan y exportan
    a ficheros .pol"""
    res = ''
    for fila in Q:
        res += '\t'.join(map(str, fila))
        res += '\n'
    return res


def guardar_matriz_Q(nombre_fichero, Q):
    guardar_fichero(nombre_fichero, generar_matriz_exportable(Q))


def leer_fichero(nombre_fichero):
    fichero = open(nombre_fichero, 'r')
    return fichero.read()


def parsear_matriz(str_Q):
    """Devuelve la matriz en numpy.array a partir de la string en el formato .pol"""
    import numpy as np
    print("'"+str_Q.split('\n')[-1]+"'")
    return np.array([[float(e) for e in row.split('\t')] for row in str_Q.split('\n') if len(row) > 0])


def leer_matriz_Q(nombre_fichero):
    return parsear_matriz(leer_fichero(nombre_fichero))


def generar_n_colores(n, pastel_factor=0, seed=8):
    random.seed(seed)
    colores = []
    for _ in range(n):
        colores.append(generate_new_color(colores, pastel_factor=pastel_factor))

    return colores


def reset_qlearning_callbacks():
    for callback in qlearning.lista_callbacks:
        callback = qlearning.vacio()


def get_nombre_ajuste(algoritmo, parametro):
    return algoritmo.get_nombre()+' - '+parametro


def formatear_ajustes_benchmark(ajustes, algoritmos, controlador):
    ajustes_dict = dict([])
    ajustes_dict[utils.AJUSTES_PARAM_N_EJECUCIONES] = int(ajustes.value(utils.AJUSTES_PARAM_N_EJECUCIONES, 10))
    ajustes_dict[utils.AJUSTES_PARAM_MODO_BENCHMARK] = ajustes.value(utils.AJUSTES_PARAM_MODO_BENCHMARK, utils.AJUSTES_BENCHMARK_MODO_BARRAS)
    for algo in algoritmos:
        ajustes_dict[algo.get_nombre()] = dict([])
        ajustes_dict[algo.get_nombre()]['alpha'] = float(ajustes.value(utils.get_nombre_ajuste(algo, 'alpha'),
                                                                       controlador.alpha))
        ajustes_dict[algo.get_nombre()]['gamma'] = float(ajustes.value(utils.get_nombre_ajuste(algo, 'gamma'),
                                                                       controlador.gamma))
        defaults = algo.get_parametros_default()
        ajustes_dict[algo.get_nombre()]['param1'] = float(ajustes.value(utils.get_nombre_ajuste(algo, 'param1'),
                                                                        defaults[0]))
        ajustes_dict[algo.get_nombre()]['param2'] = float(ajustes.value(utils.get_nombre_ajuste(algo, 'param2'),
                                                                        defaults[1]))

    print(ajustes_dict)
    return ajustes_dict


def guardar_ajustes_benchmark(ajustes, ajustes_dict, algoritmos):
    ajustes.setValue(utils.AJUSTES_PARAM_N_EJECUCIONES, ajustes_dict[utils.AJUSTES_PARAM_N_EJECUCIONES])
    ajustes.setValue(utils.AJUSTES_PARAM_MODO_BENCHMARK, ajustes_dict[utils.AJUSTES_PARAM_MODO_BENCHMARK])
    for alg in algoritmos:
        nombre = alg.get_nombre()
        for param in ['alpha', 'gamma', 'param1', 'param2']:
            ajustes.setValue(utils.get_nombre_ajuste(alg, param), ajustes_dict[nombre][param])


#  Credits to: https://gist.github.com/adewes/5884820
def get_random_color(pastel_factor=0.5):
    return [(x + pastel_factor) / (1.0 + pastel_factor) for x in [random.uniform(0, 1.0) for i in [1, 2, 3]]]


def color_distance(c1, c2):
    return sum([abs(x[0] - x[1]) for x in zip(c1, c2)])


def generate_new_color(existing_colors, pastel_factor=0.5):
    max_distance = None
    best_color = None
    for i in range(0, 100):
        color = get_random_color(pastel_factor=pastel_factor)
        if not existing_colors:
            return color
        best_distance = min([color_distance(color, c) for c in existing_colors])
        if not max_distance or best_distance > max_distance:
            max_distance = best_distance
            best_color = color
    return best_color