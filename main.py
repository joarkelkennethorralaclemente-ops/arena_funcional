
import ttkbootstrap as tb
from interfaz import ArenaApp


def main():
    ventana = tb.Window(themename="superhero")
    ArenaApp(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()