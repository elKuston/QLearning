import gym

MAPA_4X4 = 'FrozenLake-v0'
MAPA_8X8 = 'FrozenLake8x8-v0'


def make(nombre_mapa):
    return FrozenLake(nombre_mapa)


def mapas():
    return [MAPA_4X4, MAPA_8X8]


def nombres_mapas():
    return ['4x4', '8x8']


def tamanos_mapas():
    return [4, 8]


class FrozenLake:
    def __init__(self, nombre_mapa):
        self.frozen_lake = gym.make(nombre_mapa)
        self.observation_space = self.frozen_lake.observation_space
        self.action_space = self.frozen_lake.action_space

    def reset(self):
        return self.frozen_lake.reset()

    def step(self, accion):
        return self.frozen_lake.step(accion)

    def close(self):
        return self.frozen_lake.close()

    def render(self, mode):
        return self.frozen_lake.render(mode)

    @property
    def _max_episode_steps(self):
        return self.frozen_lake._max_episode_steps

    @_max_episode_steps.setter
    def _max_episode_steps(self, value):
        self.frozen_lake._max_episode_steps = value

    def get_mapa(self):
        """"
        Toma el entorno FrozenLake y lo convierte en una matriz de letras, siguiendo la misma representación que en el metodo render() del entorno: F-> casilla helada; H-> agujero;S-> Posicion inicial; G-> Posicion objetivo
        """
        mapa_str = self.render(mode='ansi')
        mapa = [[x for x in j if (x.isalpha() and x.isupper())] for j in mapa_str.split("\n") if len(j) > 0]
        return mapa

