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
