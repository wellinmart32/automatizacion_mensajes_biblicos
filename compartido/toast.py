# Archivo: toast.py
# Ruta: compartido/toast.py
# Uso: from compartido.toast import Toast
import tkinter as tk


class Toast:
    """Sistema centralizado de notificaciones toast para AutomaPro"""

    # Colores por tipo
    COLOR_INFO = "#1a73e8"        # Azul
    COLOR_EXITO = "#28a745"       # Verde
    COLOR_ADVERTENCIA = "#e65100" # Naranja
    COLOR_ERROR = "#dc3545"       # Rojo

    @staticmethod
    def info(root, mensaje, duracion=3000):
        """Toast informativo — azul, esquina inferior derecha"""
        Toast._mostrar(root, mensaje, duracion, Toast.COLOR_INFO, centro=False)

    @staticmethod
    def exito(root, mensaje, duracion=3000):
        """Toast de éxito — verde, esquina inferior derecha"""
        Toast._mostrar(root, mensaje, duracion, Toast.COLOR_EXITO, centro=False)

    @staticmethod
    def advertencia(root, mensaje, duracion=4000):
        """Toast de advertencia — naranja, esquina inferior derecha"""
        Toast._mostrar(root, mensaje, duracion, Toast.COLOR_ADVERTENCIA, centro=False)

    @staticmethod
    def error(root, mensaje, duracion=5000):
        """Toast de error — rojo, centro de pantalla, más grande"""
        Toast._mostrar(root, mensaje, duracion, Toast.COLOR_ERROR, centro=True)

    @staticmethod
    def _mostrar(root, mensaje, duracion, color, centro=False):
        """Muestra el toast con los parámetros dados"""
        try:
            toast = tk.Toplevel(root)
            toast.overrideredirect(True)
            toast.attributes('-topmost', True)

            if centro:
                ancho, alto = 420, 110
            else:
                ancho, alto = 380, 80

            frame = tk.Frame(toast, bg=color, padx=20, pady=12)
            frame.pack(fill='both', expand=True)

            font_size = 11 if centro else 10
            tk.Label(
                frame,
                text=mensaje,
                font=("Segoe UI", font_size),
                bg=color,
                fg="white",
                wraplength=ancho - 40,
                justify='center'
            ).pack()

            toast.update_idletasks()

            if centro:
                x = (root.winfo_screenwidth() // 2) - (ancho // 2)
                y = (root.winfo_screenheight() // 2) - (alto // 2)
            else:
                x = root.winfo_screenwidth() - ancho - 20
                y = root.winfo_screenheight() - alto - 60

            toast.geometry(f'{ancho}x{alto}+{x}+{y}')

            toast.after(duracion, toast.destroy)
            frame.bind('<Button-1>', lambda e: toast.destroy())

        except Exception:
            pass