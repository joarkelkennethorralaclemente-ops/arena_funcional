
from dataclasses import dataclass


@dataclass(frozen=True)
class Personaje:
    nombre: str
    vida: int
    ataque: int
    energia: int
    nivel: int = 1


@dataclass(frozen=True)
class Enemigo:
    nombre: str
    vida: int
    ataque: int


def crear_personajes_iniciales():
    return (
        Personaje("Guerrero", 100, 20, 50),
        Personaje("Mago", 80, 25, 80),
        Personaje("Arquero", 90, 18, 60),
    )


def crear_enemigo_inicial():
    return Enemigo("Dragón", 150, 15)