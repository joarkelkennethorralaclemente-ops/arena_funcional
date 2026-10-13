from pathlib import Path
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from datos import crear_personajes_iniciales, crear_enemigo_inicial
from logica import (
    procesar_accion,
    personajes_activos,
    calcular_ataque_total,
    ordenar_por_ataque,
    crear_multiplicador,
)


class ArenaApp:
    COLOR_FONDO = "#151018"
    COLOR_PANEL = "#211a26"
    COLOR_DORADO = "#f0bd58"
    COLOR_TEXTO = "#f7f0e6"
    COLOR_SUAVE = "#c6b9ca"

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Arena Funcional | La batalla del dragón")
        self.ventana.geometry("1200x850")
        self.ventana.minsize(900, 700)

        self.personajes = crear_personajes_iniciales()
        self.enemigo = crear_enemigo_inicial()
        self.historial = []
        self.mostrar_solo_activos = False
        self.potenciar_ataque = crear_multiplicador(1.5)
        self._imagen_dragon = None
        self._ventana_final = None
        self._fin_mostrado = False
        self._color_efecto_original = "warning"

        self.ventana.configure(bg=self.COLOR_FONDO)
        self.crear_interfaz()
        self.actualizar_vista()

    # ------------------------------------------------------------
    # INTERFAZ
    # ------------------------------------------------------------
    def crear_interfaz(self):
        principal = tb.Frame(self.ventana, padding=18)
        principal.pack(fill=BOTH, expand=True)

        # Cabecera de fantasía
        cabecera = tb.Frame(principal, padding=(18, 12), bootstyle="dark")
        cabecera.pack(fill=X, pady=(0, 12))

        tb.Label(
            cabecera,
            text="⚔  ARENA FUNCIONAL  ⚔",
            font=("Georgia", 24, "bold"),
            bootstyle="warning",
        ).pack()
        tb.Label(
            cabecera,
            text="EL DESAFÍO DEL DRAGÓN  •  Simulador de combate",
            font=("Helvetica", 10, "bold"),
            bootstyle="light",
        ).pack(pady=(3, 0))

        # Acciones de combate
        self.efecto_combate = tb.Label(
            principal,
            text="Elige un personaje y comienza la batalla.",
            font=("Georgia", 12, "bold"),
            bootstyle="warning",
            anchor=CENTER,
            padding=10,
        )
        self.efecto_combate.pack(fill=X, pady=(0, 8))

        panel_acciones = tb.Labelframe(
            principal, text="  ACCIONES DE COMBATE  ", padding=10, bootstyle="danger"
        )
        panel_acciones.pack(fill=X, pady=(0, 10))
        fila_acciones = tb.Frame(panel_acciones)
        fila_acciones.pack(fill=X)

        tb.Button(
            fila_acciones, text="⚔  ATACAR", bootstyle="danger",
            command=lambda: self.ejecutar("atacar"),
        ).pack(side=LEFT, expand=True, fill=X, padx=4, ipady=5)
        tb.Button(
            fila_acciones, text="✚  CURAR", bootstyle="success",
            command=lambda: self.ejecutar("curar"),
        ).pack(side=LEFT, expand=True, fill=X, padx=4, ipady=5)
        tb.Button(
            fila_acciones, text="☾  DESCANSAR", bootstyle="info",
            command=lambda: self.ejecutar("descansar"),
        ).pack(side=LEFT, expand=True, fill=X, padx=4, ipady=5)

        # Zona principal: dragón y equipo
        zona_batalla = tb.Frame(principal)
        zona_batalla.pack(fill=X, pady=(0, 12))
        zona_batalla.columnconfigure(0, weight=1, uniform="batalla")
        zona_batalla.columnconfigure(1, weight=2, uniform="batalla")

        self.panel_dragon = tb.Labelframe(
            zona_batalla,
            text="  JEFE FINAL  ",
            padding=14,
            bootstyle="danger",
        )
        self.panel_dragon.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        self.etiqueta_dragon = tb.Label(
            self.panel_dragon,
            text="🐉",
            font=("Segoe UI Emoji", 50),
            anchor=CENTER,
        )
        self.etiqueta_dragon.pack(fill=X, pady=(0, 5))
        self.cargar_imagen_dragon()

        self.nombre_dragon = tb.Label(
            self.panel_dragon,
            text=self.enemigo.nombre.upper(),
            font=("Georgia", 17, "bold"),
            bootstyle="danger",
        )
        self.nombre_dragon.pack(pady=(0, 8))

        self.vida_dragon_texto = tb.Label(
            self.panel_dragon, text="Vida: 150 / 150", font=("Helvetica", 10, "bold")
        )
        self.vida_dragon_texto.pack(anchor=W)
        self.vida_dragon_barra = tb.Progressbar(
            self.panel_dragon,
            maximum=150,
            value=150,
            bootstyle="danger-striped",
            length=240,
        )
        self.vida_dragon_barra.pack(fill=X, pady=(4, 10))

        self.ataque_dragon = tb.Label(
            self.panel_dragon, text=f"Ataque: {self.enemigo.ataque}", bootstyle="light"
        )
        self.ataque_dragon.pack(anchor=W)
        self.estado_batalla = tb.Label(
            self.panel_dragon,
            text="¡Prepárate para luchar!",
            font=("Helvetica", 10, "bold"),
            bootstyle="warning",
            wraplength=280,
            justify=CENTER,
        )
        self.estado_batalla.pack(fill=X, pady=(12, 0))

        self.panel_equipo = tb.Labelframe(
            zona_batalla,
            text="  TU EQUIPO  ",
            padding=12,
            bootstyle="warning",
        )
        self.panel_equipo.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        selector_fila = tb.Frame(self.panel_equipo)
        selector_fila.pack(fill=X, pady=(0, 8))
        tb.Label(selector_fila, text="Personaje seleccionado:").pack(side=LEFT)
        self.selector = tb.Combobox(selector_fila, state="readonly", width=18)
        self.selector.pack(side=RIGHT, padx=(8, 0))
        self.selector.bind("<<ComboboxSelected>>", lambda _evento: self.actualizar_vista())

        self.contenedor_tarjetas = tb.Frame(self.panel_equipo)
        self.contenedor_tarjetas.pack(fill=X)
        self.tarjetas_personajes = {}

        # Herramientas del simulador
        panel_herramientas = tb.Labelframe(
            principal, text="  HERRAMIENTAS  ", padding=9, bootstyle="secondary"
        )
        panel_herramientas.pack(fill=X, pady=(0, 10))
        fila_herramientas = tb.Frame(panel_herramientas)
        fila_herramientas.pack(fill=X)

        self.boton_filtro = tb.Button(
            fila_herramientas, text="Mostrar solo activos", bootstyle="secondary",
            command=self.filtrar_activos,
        )
        self.boton_filtro.pack(side=LEFT, expand=True, fill=X, padx=4)
        tb.Button(
            fila_herramientas, text="Ordenar por ataque", bootstyle="primary",
            command=self.ordenar_personajes,
        ).pack(side=LEFT, expand=True, fill=X, padx=4)
        tb.Button(
            fila_herramientas, text="Potenciar ataque ×1.5", bootstyle="warning",
            command=self.mostrar_ataque_potenciado,
        ).pack(side=LEFT, expand=True, fill=X, padx=4)
        tb.Button(
            fila_herramientas, text="Nueva batalla", bootstyle="outline-warning",
            command=self.reiniciar_batalla,
        ).pack(side=LEFT, expand=True, fill=X, padx=4)

        # Resumen + historial
        fila_inferior = tb.Frame(principal)
        fila_inferior.pack(fill=BOTH, expand=True)
        fila_inferior.columnconfigure(0, weight=1)
        fila_inferior.columnconfigure(1, weight=2)

        panel_resumen = tb.Labelframe(
            fila_inferior, text="  ESTADO DE LA ARENA  ", padding=12, bootstyle="warning"
        )
        panel_resumen.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.resumen = tb.Label(
            panel_resumen, text="", font=("Helvetica", 11, "bold"),
            justify=LEFT, wraplength=250,
        )
        self.resumen.pack(anchor=W, fill=X)
        tb.Label(
            panel_resumen,
            text="Consejo: descansa para recuperar energía y cura a tu equipo cuando lo necesite.",
            wraplength=250,
            justify=LEFT,
            bootstyle="secondary",
        ).pack(anchor=W, pady=(12, 0))

        panel_historial = tb.Labelframe(
            fila_inferior, text="  CRÓNICA DEL COMBATE  ", padding=10, bootstyle="secondary"
        )
        panel_historial.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        self.lista_historial = tb.Text(
            panel_historial, height=7, wrap="word", state="disabled", font=("Consolas", 10)
        )
        self.lista_historial.pack(fill=BOTH, expand=True)
        self.lista_historial.tag_configure("ataque", foreground="#ff8b8b")
        self.lista_historial.tag_configure("curacion", foreground="#8be0a1")
        self.lista_historial.tag_configure("normal", foreground=self.COLOR_TEXTO)

        tb.Button(
            panel_historial, text="Limpiar historial", bootstyle="outline-secondary",
            command=self.limpiar_historial,
        ).pack(anchor=E, pady=(7, 0))

    # ------------------------------------------------------------
    # IMAGEN OPCIONAL DEL DRAGÓN
    # ------------------------------------------------------------
    def cargar_imagen_dragon(self):
        base = Path(__file__).resolve().parent
        ruta = base / "imagenes" / "dragon.png"
        if not ruta.exists():
            ruta = base / "dragon.png"
        if not ruta.exists():
            return
        try:
            try:
                from PIL import Image, ImageTk
                imagen = Image.open(ruta).convert("RGBA")
                imagen.thumbnail((215, 215), Image.Resampling.NEAREST)
                self._imagen_dragon = ImageTk.PhotoImage(imagen)
            except ImportError:
                # Tk 8.6 normalmente permite PNG directamente.
                self._imagen_dragon = tk.PhotoImage(file=str(ruta))
            self.etiqueta_dragon.configure(image=self._imagen_dragon, text="", font=("Helvetica", 1))
        except (tk.TclError, OSError) as error:
            print(f"No se pudo cargar dragon.png: {error}")

    # ------------------------------------------------------------
    # ACCIONES E INTERACCIÓN
    # ------------------------------------------------------------
    def personaje_seleccionado(self):
        nombre = self.selector.get()
        return next((p for p in self.personajes if p.nombre == nombre), None)

    def ejecutar(self, accion):
        personaje = self.personaje_seleccionado()
        if personaje is None:
            self.registrar("Selecciona un personaje primero.")
            return
        if self.enemigo.vida <= 0:
            self.registrar("El dragón ya fue derrotado. Inicia una nueva batalla.")
            return

        actualizado, enemigo_actualizado, mensaje = procesar_accion(
            personaje, accion, self.enemigo
        )

        # Se conserva la inmutabilidad: se reemplaza el objeto en la tupla.
        self.personajes = tuple(
            actualizado if p.nombre == personaje.nombre else p
            for p in self.personajes
        )
        self.enemigo = enemigo_actualizado

        self.registrar(mensaje)
        self.mostrar_efecto(accion, mensaje)
        self.actualizar_vista()
        self.ventana.after(250, self.comprobar_fin_batalla)

    def mostrar_efecto(self, accion, mensaje):
        if self.enemigo.vida <= 0:
            texto, estilo = "🏆 ¡VICTORIA! El dragón ha caído.", "success"
        elif "contraataca" in mensaje.lower():
            texto, estilo = "🔥 ¡CUIDADO! El dragón contraataca.", "danger"
        elif accion == "atacar":
            texto, estilo = "⚔ ¡GOLPE CERTERO!", "danger"
        elif accion == "curar":
            texto, estilo = "✨ La magia restaura la vida.", "success"
        elif accion == "descansar":
            texto, estilo = "🌙 El personaje recupera energía.", "info"
        else:
            texto, estilo = mensaje, "warning"

        self.efecto_combate.configure(text=texto, bootstyle=estilo)
        self.panel_dragon.configure(bootstyle="danger" if accion == "atacar" else "warning")
        self.ventana.after(500, lambda: self.panel_dragon.configure(bootstyle="danger"))
        self.ventana.after(
            1800,
            lambda: self.efecto_combate.configure(
                text="Elige una acción para continuar la batalla.", bootstyle="warning"
            ),
        )

    def filtrar_activos(self):
        self.mostrar_solo_activos = not self.mostrar_solo_activos
        self.boton_filtro.configure(
            text="Mostrar todos" if self.mostrar_solo_activos else "Mostrar solo activos"
        )
        self.registrar(
            "Filtro activado: solo personajes con vida." if self.mostrar_solo_activos
            else "Se muestran todos los personajes."
        )
        self.actualizar_vista()

    def ordenar_personajes(self):
        self.personajes = ordenar_por_ataque(self.personajes)
        self.actualizar_vista()
        self.registrar("Personajes ordenados por ataque descendente.")

    def mostrar_ataque_potenciado(self):
        personaje = self.personaje_seleccionado()
        if personaje is None:
            self.registrar("Selecciona un personaje primero.")
            return
        normal = personaje.ataque
        potenciado = self.potenciar_ataque(normal)
        self.registrar(
            f"{personaje.nombre}: ataque normal = {normal}; ataque potenciado = {potenciado}."
        )
        self.efecto_combate.configure(
            text=f"✨ Poder aumentado: {normal} → {potenciado} de ataque",
            bootstyle="warning",
        )

    def reiniciar_batalla(self):
        if self._ventana_final is not None and self._ventana_final.winfo_exists():
            self._ventana_final.destroy()
        self._ventana_final = None
        self._fin_mostrado = False
        self.personajes = crear_personajes_iniciales()
        self.enemigo = crear_enemigo_inicial()
        self.historial = []
        self.mostrar_solo_activos = False
        self.boton_filtro.configure(text="Mostrar solo activos")
        self.selector.set("")
        self.lista_historial.configure(state="normal")
        self.lista_historial.delete("1.0", tk.END)
        self.lista_historial.configure(state="disabled")
        self.registrar("Nueva batalla iniciada. ¡Buena suerte, héroes!")
        self.efecto_combate.configure(text="¡Que comience el combate!", bootstyle="warning")
        self.actualizar_vista()

    def limpiar_historial(self):
        self.historial = []
        self.lista_historial.configure(state="normal")
        self.lista_historial.delete("1.0", tk.END)
        self.lista_historial.configure(state="disabled")

    # ------------------------------------------------------------
    # ACTUALIZAR TARJETAS, BARRAS Y RESUMEN
    # ------------------------------------------------------------
    def actualizar_vista(self):
        seleccionado = self.selector.get()
        visibles = personajes_activos(self.personajes) if self.mostrar_solo_activos else self.personajes
        nombres = [p.nombre for p in visibles]
        self.selector.configure(values=nombres)

        if seleccionado in nombres:
            self.selector.set(seleccionado)
        elif nombres:
            self.selector.current(0)
        else:
            self.selector.set("")

        self.dibujar_tarjetas(visibles)
        self.actualizar_dragon()

        ataque_total = calcular_ataque_total(self.personajes)
        activos = len(personajes_activos(self.personajes))
        self.resumen.configure(
            text=(
                f"Héroes: {len(self.personajes)}\n"
                f"En combate: {activos}\n"
                f"Ataque total: {ataque_total}\n"
                f"Vida del dragón: {self.enemigo.vida}/150"
            )
        )

    def dibujar_tarjetas(self, visibles):
        for widget in self.contenedor_tarjetas.winfo_children():
            widget.destroy()
        self.tarjetas_personajes = {}

        if not visibles:
            tb.Label(
                self.contenedor_tarjetas,
                text="No hay personajes activos.",
                bootstyle="danger",
            ).pack(pady=15)
            return

        for columna, personaje in enumerate(visibles):
            seleccionado = personaje.nombre == self.selector.get()
            estilo = "warning" if seleccionado else "secondary"
            tarjeta = tb.Labelframe(
                self.contenedor_tarjetas,
                text=f"  {personaje.nombre.upper()}  ",
                padding=10,
                bootstyle=estilo,
            )
            tarjeta.grid(row=0, column=columna, sticky="nsew", padx=4, pady=4)
            self.contenedor_tarjetas.columnconfigure(columna, weight=1, uniform="heroes")
            self.tarjetas_personajes[personaje.nombre] = tarjeta

            simbolos = {"Guerrero": "🛡", "Mago": "🪄", "Arquero": "🏹"}
            tb.Label(
                tarjeta, text=simbolos.get(personaje.nombre, "🧙"),
                font=("Segoe UI Emoji", 26),
            ).pack()
            tb.Label(
                tarjeta, text=f"Nivel {personaje.nivel}  •  Ataque {personaje.ataque}",
                font=("Helvetica", 9, "bold"),
            ).pack(pady=(2, 7))

            tb.Label(tarjeta, text=f"Vida  {personaje.vida}/100", font=("Helvetica", 9)).pack(anchor=W)
            vida_estilo = "success" if personaje.vida > 50 else "warning" if personaje.vida > 20 else "danger"
            tb.Progressbar(
                tarjeta, maximum=100, value=personaje.vida, bootstyle=vida_estilo,
            ).pack(fill=X, pady=(2, 7))

            tb.Label(tarjeta, text=f"Energía  {personaje.energia}/100", font=("Helvetica", 9)).pack(anchor=W)
            tb.Progressbar(
                tarjeta, maximum=100, value=personaje.energia, bootstyle="info-striped",
            ).pack(fill=X, pady=(2, 8))

            estado = "EN COMBATE" if personaje.vida > 0 else "DERROTADO"
            tb.Label(
                tarjeta, text=estado, font=("Helvetica", 8, "bold"),
                bootstyle="success" if personaje.vida > 0 else "danger",
            ).pack(pady=(0, 6))
            tb.Button(
                tarjeta,
                text="Seleccionar",
                bootstyle="warning-outline" if seleccionado else "secondary-outline",
                command=lambda nombre=personaje.nombre: self.seleccionar_personaje(nombre),
            ).pack(fill=X)

    def seleccionar_personaje(self, nombre):
        self.selector.set(nombre)
        self.actualizar_vista()

    def actualizar_dragon(self):
        vida = max(0, min(150, self.enemigo.vida))
        self.vida_dragon_barra.configure(value=vida)
        self.vida_dragon_texto.configure(text=f"Vida: {vida} / 150")
        self.nombre_dragon.configure(text=self.enemigo.nombre.upper())
        self.ataque_dragon.configure(text=f"Ataque: {self.enemigo.ataque}")
        if vida <= 0:
            self.estado_batalla.configure(text="¡El dragón ha sido derrotado!", bootstyle="success")
        else:
            self.estado_batalla.configure(text="Amenaza activa", bootstyle="danger")

    # ------------------------------------------------------------
    # HISTORIAL Y FIN DE PARTIDA
    # ------------------------------------------------------------
    def registrar(self, mensaje):
        self.historial.append(mensaje)
        texto = mensaje + "\n"
        inferior = mensaje.lower()
        etiqueta = "ataque" if any(x in inferior for x in ("daño", "atac", "contraataca", "derrotado")) else "curacion" if any(x in inferior for x in ("curó", "recuperó", "curar")) else "normal"
        self.lista_historial.configure(state="normal")
        self.lista_historial.insert(tk.END, texto, etiqueta)
        self.lista_historial.see(tk.END)
        self.lista_historial.configure(state="disabled")

    def comprobar_fin_batalla(self):
        if self._fin_mostrado:
            return
        victoria = self.enemigo.vida <= 0
        derrota = len(personajes_activos(self.personajes)) == 0
        if not victoria and not derrota:
            return
        self._fin_mostrado = True
        self.mostrar_pantalla_final(victoria)

    def mostrar_pantalla_final(self, victoria):
        self._ventana_final = tb.Toplevel(self.ventana)
        self._ventana_final.title("Resultado de la batalla")
        self._ventana_final.geometry("440x280")
        self._ventana_final.resizable(False, False)
        self._ventana_final.transient(self.ventana)
        self._ventana_final.grab_set()

        if victoria:
            icono, titulo, mensaje, estilo = "🏆", "¡VICTORIA!", "Los héroes han vencido al dragón.\nLa arena recordará esta hazaña.", "success"
        else:
            icono, titulo, mensaje, estilo = "☠", "DERROTA", "Todo el equipo ha caído.\nReúne fuerzas y vuelve a intentarlo.", "danger"

        tb.Label(self._ventana_final, text=icono, font=("Segoe UI Emoji", 42)).pack(pady=(18, 0))
        tb.Label(
            self._ventana_final, text=titulo, font=("Georgia", 22, "bold"), bootstyle=estilo,
        ).pack(pady=5)
        tb.Label(
            self._ventana_final, text=mensaje, justify=CENTER,
            font=("Helvetica", 11),
        ).pack(pady=5)
        tb.Button(
            self._ventana_final, text="Jugar otra vez", bootstyle="warning",
            command=self.reiniciar_batalla,
        ).pack(pady=(10, 15), ipadx=12)


if __name__ == "__main__":
    # Permite ejecutar interfaz.py directamente para hacer una prueba rápida.
    ventana = tb.Window(themename="superhero")
    ArenaApp(ventana)
    ventana.mainloop()
