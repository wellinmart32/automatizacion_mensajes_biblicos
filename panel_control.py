import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro


class PanelControl:
    """Panel de control principal - Mensajes Bíblicos"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📘 Mensajes Bíblicos - Panel de Control")
        self.root.geometry("700x680")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        self.root.withdraw()
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        self.gestor_licencias = GestorLicencias()
        self.licencia = self._verificar_licencia()

        if not self.licencia:
            self.root.destroy()
            return

        self._construir_ui()

    def _exe(self, nombre):
        """Retorna ruta al .exe en la misma carpeta del ejecutable"""
        if getattr(sys, 'frozen', False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, nombre)

    def _verificar_licencia(self):
        """Verifica licencia — usa caché si no hay código guardado (caso TRIAL)"""
        codigo = self.gestor_licencias.obtener_codigo_guardado()

        if not codigo:
            cache = self.gestor_licencias._obtener_cache_local()
            if cache and cache.get('valida'):
                return {
                    'valida': True,
                    'tipo': cache.get('tipo', 'TRIAL'),
                    'diasRestantes': cache.get('dias_restantes', 0),
                    'developer_permanente': cache.get('es_developer_permanente', False)
                }
            messagebox.showwarning(
                "Sin Licencia",
                "No hay licencia configurada.\n\nEjecuta el Wizard de primera vez."
            )
            return None

        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)

        if not resultado['valida']:
            messagebox.showerror("Licencia Inválida", "Tu licencia no es válida o ha expirado.")
            return None

        return resultado

    def _construir_ui(self):
        """Construye la interfaz del panel"""
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        # ==================== HEADER ====================
        header = tk.Frame(self.root, bg="#1a73e8", pady=15)
        header.pack(fill='x')

        tk.Label(
            header,
            text="📘 Mensajes Bíblicos",
            font=("Segoe UI", 20, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Badge de licencia
        if self.licencia.get('developer_permanente'):
            texto_lic = "👑 LICENCIA MAESTRA"
            color_lic = "#6f42c1"
        elif tipo_licencia == "FULL":
            texto_lic = "✅ LICENCIA COMPLETA"
            color_lic = "#28a745"
        else:
            dias = self.licencia.get('diasRestantes', 0)
            texto_lic = f"⚠️  PRUEBA — {dias} días restantes"
            color_lic = "#e65100"

        tk.Label(
            header,
            text=texto_lic,
            font=("Segoe UI", 10, "bold"),
            bg=color_lic,
            fg="white",
            padx=15,
            pady=4
        ).pack(pady=(8, 0))

        # Banner upgrade (solo TRIAL)
        if not es_full:
            banner = tk.Frame(self.root, bg="#fff3cd", pady=8)
            banner.pack(fill='x')
            tk.Label(
                banner,
                text="🔓 Desbloquea WhatsApp, tareas automáticas y más con la versión Completa",
                font=("Segoe UI", 9),
                bg="#fff3cd",
                fg="#856404"
            ).pack(side='left', padx=(15, 10))
            tk.Button(
                banner,
                text="⬆️ Comprar versión Completa",
                font=("Segoe UI", 9, "bold"),
                bg="#ffc107",
                fg="#212529",
                cursor="hand2",
                relief='flat',
                padx=10,
                command=self._abrir_upgrade
            ).pack(side='right', padx=(0, 15))

        # ==================== GRID PRINCIPAL ====================
        container = tk.Frame(self.root, bg="#f0f0f0")
        container.pack(fill='both', expand=True, padx=25, pady=15)

        grid = tk.Frame(container, bg="#f0f0f0")
        grid.pack(fill='both', expand=True)

        # Fila 0
        self._boton(grid, "⚡\nAcciones", "Publicar y automatizar",
                    self._abrir_acciones, row=0, col=0, color="#e65100")
        self._boton(grid, "⚙️\nConfigurador", "Ajustar configuración",
                    self._abrir_configurador, row=0, col=1)

        # Fila 1
        self._boton(grid, "📝\nMensajes", "Crear y editar mensajes",
                    self._abrir_gestor_mensajes, row=1, col=0)
        self._boton(grid, "📊\nEstadísticas", "Ver historial",
                    self._ver_estadisticas, row=1, col=1)

        # Fila 2
        if es_full:
            self._boton(grid, "🗓️\nTareas Automáticas", "Programar publicaciones",
                        self._gestionar_tareas, row=2, col=0, color="#28a745")
        else:
            self._boton(grid, "🔒\nTareas Automáticas", "Solo versión Completa",
                        self._mostrar_mensaje_upgrade, row=2, col=0, color="#9e9e9e")

        self._boton(grid, "❓\nAyuda", "Cómo usar el sistema",
                    self._mostrar_ayuda, row=2, col=1)

        # Fila 3
        self._boton(grid, "❌\nSalir", "Cerrar panel",
                    self.root.destroy, row=3, col=0, color="#dc3545")

    def _boton(self, parent, texto, subtexto, comando, row, col, color="#1a73e8"):
        """Crea un botón estilizado en el grid"""
        frame = tk.Frame(parent, bg="white", relief='solid', borderwidth=1, cursor="hand2")
        frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

        lbl1 = tk.Label(frame, text=texto, font=("Segoe UI", 13, "bold"), bg="white", fg=color)
        lbl1.pack(expand=True, pady=(12, 3))

        lbl2 = tk.Label(frame, text=subtexto, font=("Segoe UI", 8), bg="white", fg="gray")
        lbl2.pack(expand=True, pady=(0, 12))

        for w in [frame, lbl1, lbl2]:
            w.bind('<Button-1>', lambda e, c=comando: c())
            w.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
            w.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))

    # ==================== VENTANA ACCIONES ====================

    def _abrir_acciones(self):
        """Abre ventana de acciones disponibles según licencia"""
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        ventana = tk.Toplevel(self.root)
        ventana.title("⚡ Acciones")
        ventana.geometry("500x420")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        ventana.withdraw()
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - 250
        y = (ventana.winfo_screenheight() // 2) - 210
        ventana.geometry(f'500x420+{x}+{y}')
        ventana.deiconify()

        # Header
        header = tk.Frame(ventana, bg="#e65100", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="⚡ Acciones",
            font=("Segoe UI", 14, "bold"),
            bg="#e65100",
            fg="white"
        ).pack()
        tk.Label(
            header,
            text="Selecciona qué deseas ejecutar",
            font=("Segoe UI", 9),
            bg="#e65100",
            fg="white"
        ).pack()

        frame = tk.Frame(ventana, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=20, pady=15)

        # Verificar predicaciones pendientes
        cola = os.path.join(
            os.path.dirname(self._exe("MensajesBiblicos.exe")),
            "cola-facebook", "pendientes"
        )
        hay_predicaciones = os.path.exists(cola) and len(os.listdir(cola)) > 0

        # Acción 1 — siempre disponible
        tk.Button(
            frame,
            text="▶️  Publicar Mensaje Bíblico en Facebook",
            font=("Segoe UI", 11, "bold"),
            bg="#1a73e8",
            fg="white",
            activebackground="#155ab6",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=lambda: [ventana.destroy(), self._publicar_facebook()]
        ).pack(fill='x', pady=(0, 8))

        # Acción 2 — Enviar Oraciones por WhatsApp
        if es_full:
            tk.Button(
                frame,
                text="📱  Enviar Oraciones por WhatsApp",
                font=("Segoe UI", 11, "bold"),
                bg="#25D366",
                fg="white",
                activebackground="#1da851",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=lambda: [ventana.destroy(), self._enviar_oraciones()]
            ).pack(fill='x', pady=(0, 8))
        else:
            tk.Button(
                frame,
                text="🔒  Enviar Oraciones por WhatsApp — Solo versión Completa",
                font=("Segoe UI", 11),
                bg="#e0e0e0",
                fg="#9e9e9e",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=self._mostrar_mensaje_upgrade
            ).pack(fill='x', pady=(0, 8))

        # Acción 3 — Extraer Predicaciones de WhatsApp
        if es_full:
            tk.Button(
                frame,
                text="🎬  Extraer Predicaciones de WhatsApp",
                font=("Segoe UI", 11, "bold"),
                bg="#25D366",
                fg="white",
                activebackground="#1da851",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=lambda: [ventana.destroy(), self._extraer_predicaciones()]
            ).pack(fill='x', pady=(0, 8))
        else:
            tk.Button(
                frame,
                text="🔒  Extraer Predicaciones de WhatsApp — Solo versión Completa",
                font=("Segoe UI", 11),
                bg="#e0e0e0",
                fg="#9e9e9e",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=self._mostrar_mensaje_upgrade
            ).pack(fill='x', pady=(0, 8))

        # Acción 4 — Publicar Predicaciones en Facebook
        if es_full:
            color_pred = "#1a73e8" if hay_predicaciones else "#90a4ae"
            cmd_pred = (lambda: [ventana.destroy(), self._publicar_predicaciones()]) \
                       if hay_predicaciones else self._sin_predicaciones
            tk.Button(
                frame,
                text="📤  Publicar Predicaciones en Facebook",
                font=("Segoe UI", 11, "bold"),
                bg=color_pred,
                fg="white",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=cmd_pred
            ).pack(fill='x', pady=(0, 8))
        else:
            tk.Button(
                frame,
                text="🔒  Publicar Predicaciones en Facebook — Solo versión Completa",
                font=("Segoe UI", 11),
                bg="#e0e0e0",
                fg="#9e9e9e",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=self._mostrar_mensaje_upgrade
            ).pack(fill='x', pady=(0, 8))

        tk.Button(
            frame,
            text="Cerrar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            command=ventana.destroy
        ).pack(pady=(10, 0))

    # ==================== ACCIONES ====================

    def _publicar_facebook(self):
        try:
            exe = self._exe("MensajesBiblicos.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, "flujo_completo_facebook.py"])
            self._toast("✅ Publicación iniciada", "El navegador se abrirá en unos segundos...")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar la publicación:\n{e}")

    def _enviar_oraciones(self):
        try:
            exe = self._exe("OracionesWhatsApp.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable,
                                  os.path.join("publicadores", "whatsapp_oracion.py")])
            self._toast("📱 Oraciones WhatsApp", "Iniciando envío de llamados de oración...")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar el módulo:\n{e}")

    def _extraer_predicaciones(self):
        try:
            exe = self._exe("ExtractorPredicaciones.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, "extraer_predicaciones_whatsapp.py"])
            self._toast("🎬 Extrayendo predicaciones", "Iniciando extracción de WhatsApp...")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar el módulo:\n{e}")

    def _publicar_predicaciones(self):
        try:
            exe = self._exe("MensajesBiblicos.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe, "--modulo", "publicar_predicaciones"])
            else:
                subprocess.Popen([sys.executable, "flujo_completo_facebook.py",
                                  "--solo-predicaciones"])
            self._toast("📤 Publicando predicaciones", "Publicando en Facebook...")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo publicar:\n{e}")

    def _sin_predicaciones(self):
        messagebox.showinfo(
            "Sin predicaciones",
            "No hay predicaciones extraídas.\n\n"
            "Primero usa 'Extraer Predicaciones de WhatsApp'\n"
            "y luego podrás publicarlas en Facebook."
        )

    def _abrir_configurador(self):
        try:
            exe = self._exe("ConfiguradorMensajes.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, "configurador_gui.py"])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el configurador:\n{e}")

    def _abrir_gestor_mensajes(self):
        try:
            exe = self._exe("GestorMensajes.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, "gestor_mensajes_gui.py"])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor:\n{e}")

    def _gestionar_tareas(self):
        try:
            exe = self._exe("GestorTareasMensajes.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, "gestor_tareas_gui.py"])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor de tareas:\n{e}")

    def _abrir_upgrade(self):
        """Abre la página de compra — pendiente de URL real"""
        messagebox.showinfo(
            "⬆️ Versión Completa",
            "Para adquirir la versión Completa visita:\n\nautomapro.com\n\n"
            "Desbloquea WhatsApp, tareas automáticas y publicación de predicaciones."
        )

    def _mostrar_mensaje_upgrade(self):
        """Muestra mensaje cuando el usuario intenta acceder a función premium"""
        messagebox.showinfo(
            "🔒 Función Premium",
            "Esta función está disponible solo en la versión Completa.\n\n"
            "Adquiérela en automapro.com para desbloquear:\n"
            "• Enviar Oraciones por WhatsApp\n"
            "• Extraer Predicaciones de WhatsApp\n"
            "• Publicar Predicaciones en Facebook\n"
            "• Tareas Automáticas"
        )

    def _ver_estadisticas(self):
        """Muestra ventana de estadísticas"""
        try:
            gestor = GestorRegistro()
            stats = gestor.registro.get('estadisticas', {})
            fecha_ultima = gestor.registro.get('ultima_publicacion', {}).get('fecha', 'Nunca')

            ventana = tk.Toplevel(self.root)
            ventana.title("📊 Estadísticas")
            ventana.geometry("400x370")
            ventana.resizable(False, False)
            ventana.configure(bg="#f0f0f0")
            ventana.withdraw()
            ventana.update_idletasks()
            x = (ventana.winfo_screenwidth() // 2) - 200
            y = (ventana.winfo_screenheight() // 2) - 185
            ventana.geometry(f'400x370+{x}+{y}')
            ventana.deiconify()

            header = tk.Frame(ventana, bg="#1a73e8", pady=12)
            header.pack(fill='x')
            tk.Label(header, text="📊 Estadísticas del Sistema",
                     font=("Segoe UI", 13, "bold"), bg="#1a73e8", fg="white").pack()

            frame = tk.Frame(ventana, bg="white", padx=25, pady=15)
            frame.pack(fill='both', expand=True, padx=15, pady=15)

            items = [
                ("📈 Total publicaciones:", str(stats.get('total_publicaciones', 0))),
                ("✅ Exitosas:", str(stats.get('publicaciones_exitosas', 0))),
                ("❌ Fallidas:", str(stats.get('publicaciones_fallidas', 0))),
                ("🎯 Tasa de éxito:", f"{stats.get('tasa_exito', 0):.1f}%"),
                ("⏱️ Tiempo promedio:", f"{stats.get('tiempo_promedio', 0):.1f}s"),
                ("📅 Última publicación:", fecha_ultima),
            ]

            for label, valor in items:
                row = tk.Frame(frame, bg="white")
                row.pack(fill='x', pady=5)
                tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                         bg="white", anchor='w', width=25).pack(side='left')
                tk.Label(row, text=valor, font=("Segoe UI", 10),
                         bg="white", anchor='w').pack(side='left')

            tk.Button(
                ventana,
                text="Cerrar",
                font=("Segoe UI", 10),
                bg="#6c757d",
                fg="white",
                width=12,
                command=ventana.destroy
            ).pack(pady=15)

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error mostrando estadísticas:\n{e}")

    def _mostrar_ayuda(self):
        messagebox.showinfo("❓ Ayuda - Mensajes Bíblicos",
            "📘 GUÍA RÁPIDA\n\n"
            "⚡ ACCIONES\n"
            "   Publicar Mensaje Bíblico → publica mensaje en Facebook\n"
            "   Enviar Oraciones por WhatsApp → envía llamados de oración\n"
            "   Extraer Predicaciones → trae mensajes de tu grupo\n"
            "   Publicar Predicaciones → sube lo extraído a Facebook\n\n"
            "⚙ GESTIÓN\n"
            "   Configurador → ajusta navegador, tiempos y módulos\n"
            "   Mensajes → crea y edita tus mensajes bíblicos\n"
            "   Estadísticas → consulta el historial\n"
            "   Tareas Automáticas → programa publicaciones (Completa)"
        )

    def _toast(self, titulo, mensaje, duracion=3000, color="#28a745"):
        """Notificación toast que se cierra sola"""
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        ancho, alto = 350, 90
        x = toast.winfo_screenwidth() - ancho - 20
        y = toast.winfo_screenheight() - alto - 60
        toast.geometry(f'{ancho}x{alto}+{x}+{y}')
        frame = tk.Frame(toast, bg=color, relief='raised', borderwidth=2)
        frame.pack(fill='both', expand=True)
        tk.Label(frame, text=titulo, font=("Segoe UI", 11, "bold"),
                 bg=color, fg="white").pack(pady=(10, 3))
        tk.Label(frame, text=mensaje, font=("Segoe UI", 9),
                 bg=color, fg="white", wraplength=300).pack(pady=(0, 10))
        toast.after(duracion, toast.destroy)
        frame.bind('<Button-1>', lambda e: toast.destroy())

    def ejecutar(self):
        self.root.mainloop()


def main():
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main()