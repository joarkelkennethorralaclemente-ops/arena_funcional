# Bitácora de uso de IA
## Arena Funcional: La batalla del dragón

Este documento registra el apoyo de ChatGPT en el proyecto. Los prompts entre comillas corresponden a mensajes conservados en la conversación; los demás son resúmenes de solicitudes previas, no citas textuales.

## 1. Herramienta utilizada
Se utilizó ChatGPT para orientar el desarrollo de la interfaz, la lógica del combate, la documentación y la publicación en GitHub. El código debe revisarse y comprenderse antes de entregarlo.

## 2. Prompts usados
| Solicitud | Propósito |
|---|---|
| Pedir que el dragón contraatacara (resumen) | Incorporar respuesta del enemigo después de las acciones. |
| Pedir una interfaz de fantasía (resumen) | Mejorar presentación visual. |
| Pedir integrar el dragón pixelado verde de tres cabezas (resumen) | Mostrar una imagen personalizada. |
| «ya salio mi dragon pero se me borraron las opciones de atacar y que mi dragon ataque tambien» | Corregir visibilidad de botones y contraataque. |

# 3. Fragmentos sugeridos por IA

# A. Contraataque del dragón
Se propuso una función separada de los eventos de la interfaz:

```python
def contraataque_dragon(personaje, enemigo, mensaje):
    # Aplica la respuesta del dragón si corresponde.
    # Devuelve los estados actualizados y un mensaje.
```

Este fragmento es **ilustrativo**, no una transcripción exacta. El código definitivo está en `logica.py`.

**Aceptado:** separar el contraataque en una función de lógica.  
**Modificado:** integrarlo en `procesar_accion()` para que la respuesta ocurra durante el turno, sin depender de un botón específico.  
**Por qué:** mantiene la separación de capas.

# B. Actualización inmutable
Se explicó este patrón:

```python
from dataclasses import replace

def recibir_danio(personaje, cantidad):
    nueva_vida = max(0, personaje.vida - max(0, cantidad))
    return replace(personaje, vida=nueva_vida)
```

**Aceptado:** utilizar `replace()` para devolver un nuevo personaje.  
**Por qué:** evita modificar directamente el estado original.

### C. Presentación visual
La IA sugirió una interfaz con `tkinter` y `ttkbootstrap`, tarjetas de héroes, barras de vida y una imagen `imagenes/dragon.png`.

**Aceptado:** estilo visual y recurso gráfico.  
**Modificado:** tamaño de la imagen y ubicación de botones.  
**Por qué:** una versión anterior ocultaba «Atacar», «Curar» y «Descansar».

# 4. Qué se aceptó
- Separación entre `datos.py`, `logica.py`, `interfaz.py` y `main.py`.
- Funciones específicas para daño, curación y contraataque.
- Uso de estructuras inmutables con `dataclass(frozen=True)` y `replace()`.
- Integración del dragón pixelado y mejoras visuales.
- Preparación de `requisitos.txt` y `analisis-funcional.md`.

# 5. Qué se modificó
- **Interfaz:** los botones se reorganizaron para que permanecieran visibles después de incorporar la imagen.
- **Combate:** se agregó la respuesta del dragón a la secuencia de acciones.
- **Archivos:** se organizó el recurso gráfico en `imagenes/` y se revisó la instalación de dependencias.

# 6. Qué se rechazó y por qué
Se **descartó la distribución anterior de la interfaz** que ocultaba los botones de combate, porque dificultaba usar el juego.

No consta en los mensajes disponibles otro rechazo explícito de una sugerencia concreta de IA. Como criterio técnico, tampoco conviene poner toda la lógica dentro de callbacks o usar una sola `lambda` para reglas extensas: esas decisiones reducirían la claridad y dificultarían el mantenimiento. Esto último es un criterio de diseño, no una afirmación de que la IA haya sugerido hacerlo.

# 7. Correcciones y verificaciones
1. Se detectó que el dragón se mostraba, pero las acciones de combate no quedaban visibles.
2. Se preparó una interfaz reorganizada y una función de contraataque.
3. Se probó por separado un caso de ataque y contraataque en la lógica; esto no equivale a probar toda la GUI.
4. Se verificó en la terminal que `ttkbootstrap` y `Pillow` estaban instalados.
5. Se corrigió la ubicación de la carpeta de trabajo para ejecutar `pip install -r requisitos.txt`.
6. Se solucionó un error 403 de GitHub cambiando el destino del repositorio a la cuenta autorizada.
7. El comando `git push -u origin main` confirmó la publicación de la rama `main`.

# 8. Aprendizajes técnicos
El proyecto permitió trabajar la separación entre interfaz, reglas y datos; la actualización inmutable de personajes; las funciones puras e impuras; el manejo de imágenes; las dependencias de Python; y el uso de Git y GitHub.

También se observó que una respuesta de IA puede requerir correcciones: al agregar el dragón visualmente, hubo que reorganizar la pantalla para recuperar los botones. Por eso es importante revisar y probar las propuestas antes de entregarlas.

# 9. Reflexión
La IA fue una herramienta de apoyo, no un reemplazo de la comprensión técnica. Para defender el proyecto se debe poder explicar cómo funciona cada parte, qué decisiones se tomaron y qué errores se corrigieron.

