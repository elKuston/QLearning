FORMATO_FICHERO = '.pol'


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
