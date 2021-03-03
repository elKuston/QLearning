from PyQt5.QtCore import QRunnable

class SegundoPlano(QRunnable):
    def __init__(self, funcion, *argumentos, **kwargumentos):
        super().__init__()
        self.funcion = funcion
        self.argumentos = argumentos
        self.kwargumentos = kwargumentos

    def run(self) -> None:
        self.funcion(*self.argumentos, **self.kwargumentos)
