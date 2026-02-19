import os
import configparser
import tkinter as tk
from tkinter import ttk, messagebox


class ConfiguradorGUI:
    """Interfaz gráfica para configurar el sistema de Mensajes Bíblicos"""

    def __init__(self):
        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()
        self.cambios = {}

        self.root = tk.Tk()
        self.root.title("⚙️ Configurador - Mensajes Bíblicos")
        self.root.geometry("600x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Ocultar ventana mientras se configura
        self.root.withdraw()
        
        # Centrar ventana correctamente
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Mostrar ventana ya centrada
        self.root.deiconify()

        self._cargar_config()
        self._construir_ui()

    def _cargar_config(self):
        """Carga la configuración desde archivo"""
        if os.path.exists(self.archivo_config):
            self.config.read(self.archivo_config, encoding='utf-8')

    def _guardar_config(self):
        """Guarda los cambios en el archivo"""
        try:
            # Aplicar valores de la GUI al config
            # General
            self.config['GENERAL']['carpeta_mensajes'] = self.var_carpeta.get()
            self.config['GENERAL']['navegador'] = self.var_navegador.get()

            # Mensajes
            self.config['MENSAJES']['seleccion'] = self.var_seleccion.get()
            self.config['MENSAJES']['historial_evitar_repetir'] = self.var_historial.get()
            self.config['MENSAJES']['agregar_hashtags'] = self.var_hashtags.get()
            self.config['MENSAJES']['hashtags'] = self.var_hashtags_texto.get()

            # Publicación
            self.config['PUBLICACION']['tiempo_entre_intentos'] = self.var_tiempo_intentos.get()
            self.config['PUBLICACION']['max_intentos_por_publicacion'] = self.var_max_intentos.get()
            self.config['PUBLICACION']['espera_despues_publicar'] = self.var_espera.get()

            # WhatsApp
            if not self.config.has_section('PREDICACIONES'):
                self.config.add_section('PREDICACIONES')
            self.config['PREDICACIONES']['nombre_grupo_whatsapp'] = self.var_grupo_whatsapp.get()
            self.config['PREDICACIONES']['mensajes_por_extraccion'] = self.var_mensajes_extraccion.get()
            self.config['PREDICACIONES']['alternar_con_predicaciones'] = self.var_alternar.get()

            # Navegador
            self.config['NAVEGADOR']['usar_perfil_existente'] = self.var_usar_perfil.get()
            self.config['NAVEGADOR']['maximizar_ventana'] = self.var_maximizar.get()

            # Límites
            self.config['LIMITES']['tiempo_minimo_entre_publicaciones_segundos'] = self.var_tiempo_minimo.get()
            self.config['LIMITES']['permitir_forzar_publicacion_manual'] = self.var_forzar_manual.get()

            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                f.write("# ============================================================\n")
                f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR AUTOMÁTICO FACEBOOK\n")
                f.write("# ============================================================\n\n")
                self.config.write(f)

            messagebox.showinfo("✅ Éxito", "Configuración guardada correctamente")
            self.root.destroy()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _get(self, seccion, clave, defecto=''):
        """Obtiene un valor del config de forma segura"""
        try:
            return self.config[seccion][clave].split('#')[0].strip()
        except:
            return defecto

    def _construir_ui(self):
        """Construye la interfaz gráfica"""

        # Header
        header = tk.Frame(self.root, bg="#1a73e8", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="⚙️  Configurador - Mensajes Bíblicos",
            font=("Segoe UI", 14, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Notebook (pestañas)
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Segoe UI', 9))

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # ==================== PESTAÑA GENERAL ====================
        tab_general = ttk.Frame(notebook)
        notebook.add(tab_general, text="⚙️ General")

        self._seccion(tab_general, "📁 Carpeta de mensajes (.txt)")
        self.var_carpeta = tk.StringVar(value=self._get('GENERAL', 'carpeta_mensajes', 'mensajes'))
        tk.Entry(tab_general, textvariable=self.var_carpeta, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_general, "🌐 Navegador")
        self.var_navegador = tk.StringVar(value=self._get('GENERAL', 'navegador', 'firefox'))
        frame_nav = tk.Frame(tab_general, bg="#f0f0f0")
        frame_nav.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['firefox', 'chrome']:
            tk.Radiobutton(
                frame_nav, text=opcion.capitalize(),
                variable=self.var_navegador, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== PESTAÑA MENSAJES ====================
        tab_mensajes = ttk.Frame(notebook)
        notebook.add(tab_mensajes, text="📝 Mensajes")

        self._seccion(tab_mensajes, "🎲 Método de selección")
        self.var_seleccion = tk.StringVar(value=self._get('MENSAJES', 'seleccion', 'aleatorio'))
        frame_sel = tk.Frame(tab_mensajes, bg="#f0f0f0")
        frame_sel.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['aleatorio', 'secuencial']:
            tk.Radiobutton(
                frame_sel, text=opcion.capitalize(),
                variable=self.var_seleccion, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_mensajes, "💾 Memoria: últimos N mensajes a evitar repetir")
        self.var_historial = tk.StringVar(value=self._get('MENSAJES', 'historial_evitar_repetir', '5'))
        tk.Spinbox(tab_mensajes, from_=0, to=20, textvariable=self.var_historial, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_mensajes, "# Agregar hashtags automáticamente")
        self.var_hashtags = tk.StringVar(value=self._get('MENSAJES', 'agregar_hashtags', 'no'))
        frame_ht = tk.Frame(tab_mensajes, bg="#f0f0f0")
        frame_ht.pack(anchor='w', padx=20, pady=(0, 6))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_ht, text=label,
                variable=self.var_hashtags, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_mensajes, "📌 Hashtags (separados por comas)")
        self.var_hashtags_texto = tk.StringVar(value=self._get('MENSAJES', 'hashtags', '#Fe,#Biblia'))
        tk.Entry(tab_mensajes, textvariable=self.var_hashtags_texto, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        # ==================== PESTAÑA PUBLICACIÓN ====================
        tab_pub = ttk.Frame(notebook)
        notebook.add(tab_pub, text="🚀 Publicación")

        self._seccion(tab_pub, "⏱️ Tiempo entre intentos (segundos)")
        self.var_tiempo_intentos = tk.StringVar(value=self._get('PUBLICACION', 'tiempo_entre_intentos', '3'))
        tk.Spinbox(tab_pub, from_=1, to=30, textvariable=self.var_tiempo_intentos, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "🔄 Máximo de intentos por publicación")
        self.var_max_intentos = tk.StringVar(value=self._get('PUBLICACION', 'max_intentos_por_publicacion', '3'))
        tk.Spinbox(tab_pub, from_=1, to=10, textvariable=self.var_max_intentos, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pub, "⏳ Espera después de publicar (segundos)")
        self.var_espera = tk.StringVar(value=self._get('PUBLICACION', 'espera_despues_publicar', '5'))
        tk.Spinbox(tab_pub, from_=1, to=30, textvariable=self.var_espera, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        # ==================== PESTAÑA WHATSAPP ====================
        tab_wa = ttk.Frame(notebook)
        notebook.add(tab_wa, text="📱 WhatsApp")

        self._seccion(tab_wa, "👥 Nombre del grupo de WhatsApp")
        tk.Label(tab_wa, text="⚠️  Debe ser EXACTAMENTE igual a como aparece en WhatsApp",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_grupo_whatsapp = tk.StringVar(value=self._get('PREDICACIONES', 'nombre_grupo_whatsapp', 'Prédicas'))
        tk.Entry(tab_wa, textvariable=self.var_grupo_whatsapp, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_wa, "📦 Predicaciones a extraer por vez")
        self.var_mensajes_extraccion = tk.StringVar(value=self._get('PREDICACIONES', 'mensajes_por_extraccion', '10'))
        tk.Spinbox(tab_wa, from_=1, to=50, textvariable=self.var_mensajes_extraccion, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_wa, "🔀 Alternar mensajes bíblicos con predicaciones")
        tk.Label(tab_wa, text="si = publica 1 bíblico, 1 predicación, 1 bíblico...",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_alternar = tk.StringVar(value=self._get('PREDICACIONES', 'alternar_con_predicaciones', 'si'))
        frame_alt = tk.Frame(tab_wa, bg="#f0f0f0")
        frame_alt.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_alt, text=label,
                variable=self.var_alternar, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== PESTAÑA NAVEGADOR ====================
        tab_nav = ttk.Frame(notebook)
        notebook.add(tab_nav, text="🌐 Navegador")

        self._seccion(tab_nav, "👤 Usar perfil existente del navegador")
        tk.Label(tab_nav, text="si = usa tu sesión de Facebook guardada",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_usar_perfil = tk.StringVar(value=self._get('NAVEGADOR', 'usar_perfil_existente', 'si'))
        frame_perfil = tk.Frame(tab_nav, bg="#f0f0f0")
        frame_perfil.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_perfil, text=label,
                variable=self.var_usar_perfil, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_nav, "🖥️ Maximizar ventana al iniciar")
        self.var_maximizar = tk.StringVar(value=self._get('NAVEGADOR', 'maximizar_ventana', 'si'))
        frame_max = tk.Frame(tab_nav, bg="#f0f0f0")
        frame_max.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_max, text=label,
                variable=self.var_maximizar, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== PESTAÑA LÍMITES ====================
        tab_lim = ttk.Frame(notebook)
        notebook.add(tab_lim, text="🔒 Límites")

        self._seccion(tab_lim, "⏰ Tiempo mínimo entre publicaciones (segundos)")
        tk.Label(tab_lim, text="Evita duplicados si se ejecuta 2 veces seguidas",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_tiempo_minimo = tk.StringVar(value=self._get('LIMITES', 'tiempo_minimo_entre_publicaciones_segundos', '120'))
        tk.Spinbox(tab_lim, from_=30, to=600, textvariable=self.var_tiempo_minimo, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_lim, "🔓 Permitir forzar publicación manual")
        tk.Label(tab_lim, text="si = permite saltarse el tiempo mínimo en ejecución manual",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_forzar_manual = tk.StringVar(value=self._get('LIMITES', 'permitir_forzar_publicacion_manual', 'si'))
        frame_forzar = tk.Frame(tab_lim, bg="#f0f0f0")
        frame_forzar.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame_forzar, text=label,
                variable=self.var_forzar_manual, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        # ==================== BOTONES ====================
        frame_botones = tk.Frame(self.root, bg="#f0f0f0", pady=8)
        frame_botones.pack(fill='x', padx=10)

        tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=14,
            command=self.root.destroy
        ).pack(side='right', padx=5)

        tk.Button(
            frame_botones,
            text="💾 Guardar",
            font=("Segoe UI", 10, "bold"),
            bg="#1a73e8",
            fg="white",
            width=14,
            command=self._guardar_config
        ).pack(side='right', padx=5)

    def _seccion(self, parent, texto):
        """Crea un label de sección"""
        tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0",
            fg="#333"
        ).pack(anchor='w', padx=20, pady=(12, 2))

    def ejecutar(self):
        """Inicia la interfaz gráfica"""
        self.root.mainloop()


def main():
    app = ConfiguradorGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()