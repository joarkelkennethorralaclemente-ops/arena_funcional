
from dataclasses import replace
from functools import reduce

from datos import Personaje, Enemigo


def recibir_danio(personaje, cantidad):
    nueva_vida = max(0, personaje.vida - max(0, cantidad))
    return replace(personaje, vida=nueva_vida)


def curar_personaje(personaje, cantidad=20):
    nueva_vida = min(100, personaje.vida + max(0, cantidad))
    return replace(personaje, vida=nueva_vida)


def esta_activo(personaje):
    return personaje.vida > 0


def contraataque_dragon(personaje, enemigo, mensaje):
    """El dragón responde a una acción válida si sigue con vida."""
    if enemigo.vida <= 0 or not esta_activo(personaje):
        return personaje, enemigo, mensaje
    actualizado = recibir_danio(personaje, enemigo.ataque)
    mensaje += (f"\n¡El {enemigo.nombre} contraataca! "
                f"Causa {enemigo.ataque} de daño a {personaje.nombre}. "
                f"Vida restante: {actualizado.vida}.")
    if actualizado.vida == 0:
        mensaje += f" ¡{personaje.nombre} ha sido derrotado!"
    return actualizado, enemigo, mensaje


def procesar_accion(personaje, accion, enemigo):
    match accion:
        case "atacar":
            if not esta_activo(personaje):
                return personaje, enemigo, "El personaje está fuera de combate."

            if enemigo.vida <= 0:
                return personaje, enemigo, "El enemigo ya fue derrotado."

            if personaje.energia < 10:
                return personaje, enemigo, "No hay energía suficiente."

            actualizado = replace(
                personaje,
                energia=personaje.energia - 10
            )

            enemigo_actualizado = recibir_danio(enemigo, personaje.ataque)

            mensaje = (
                f"{personaje.nombre} causó {personaje.ataque} de daño "
                f"al {enemigo.nombre}. "
                f"Vida restante del enemigo: {enemigo_actualizado.vida}."
            )

            if enemigo_actualizado.vida == 0:
                mensaje += " ¡El enemigo ha sido derrotado!"

            return contraataque_dragon(actualizado, enemigo_actualizado, mensaje)

        case "curar":
            if not esta_activo(personaje):
                return personaje, enemigo, "El personaje está fuera de combate."

            if personaje.vida >= 100:
                return personaje, enemigo, "La vida ya está al máximo."

            actualizado = curar_personaje(personaje)

            return contraataque_dragon(
                actualizado, enemigo,
                f"{personaje.nombre} recuperó vida. Vida actual: {actualizado.vida}."
            )

        case "descansar":
            if not esta_activo(personaje):
                return personaje, enemigo, "El personaje está fuera de combate."

            actualizado = replace(
                personaje,
                energia=min(100, personaje.energia + 20)
            )

            return contraataque_dragon(
                actualizado, enemigo,
                f"{personaje.nombre} recuperó energía. Energía actual: {actualizado.energia}."
            )

        case _:
            return personaje, enemigo, "Acción desconocida."


def crear_multiplicador(factor):
    def aplicar(valor):
        return round(valor * factor)

    return aplicar


def transformar_personajes(personajes, transformacion):
    return tuple(map(transformacion, personajes))


def personajes_activos(personajes):
    return tuple(filter(esta_activo, personajes))


def ordenar_por_ataque(personajes):
    return tuple(
        sorted(personajes, key=lambda p: p.ataque, reverse=True)
    )


def calcular_ataque_total(personajes):
    return reduce(lambda total, p: total + p.ataque, personajes, 0)


def puede_atacar(personaje):
    return esta_activo(personaje) and personaje.energia >= 10