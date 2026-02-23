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
        self.root.geometry("620x560")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Centrar antes de mostrar
        self.root.withdraw()
        self.root.update_idletasks()
        width = 620
        height = 560
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
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
            # Facebook — carpeta_mensajes no se toca, es fija
            self.config['GENERAL']['navegador'] = self.var_nav_facebook.get()

            # Mensajes
            sel = self.var_seleccion.get()
            self.config['MENSAJES']['seleccion'] = sel if sel else 'aleatorio'
            self.config['MENSAJES']['historial_evitar_repetir'] = self.var_historial.get()
            self.config['MENSAJES']['agregar_hashtags'] = self.var_hashtags.get()
            self.config['MENSAJES']['hashtags'] = self.var_hashtags_texto.get()

            # Publicación
            self.config['PUBLICACION']['tiempo_entre_intentos'] = self.var_tiempo_intentos.get()
            self.config['PUBLICACION']['max_intentos_por_publicacion'] = self.var_max_intentos.get()
            self.config['PUBLICACION']['espera_despues_publicar'] = self.var_espera.get()

            # Predicaciones
            if not self.config.has_section('PREDICACIONES'):
                self.config.add_section('PREDICACIONES')
            self.config['PREDICACIONES']['nombre_grupo_whatsapp'] = self.var_grupo_predicaciones.get()
            self.config['PREDICACIONES']['mensajes_por_extraccion'] = self.var_mensajes_extraccion.get()
            self.config['PREDICACIONES']['alternar_con_predicaciones'] = self.var_alternar.get()
            self.config['PREDICACIONES']['navegador'] = self.var_nav_predicaciones.get()

            # Oraciones
            if not self.config.has_section('ORACIONES'):
                self.config.add_section('ORACIONES')
            self.config['ORACIONES']['navegador'] = self.var_nav_oraciones.get()

            # Navegador general
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
            valor = self.config[seccion][clave].split('#')[0].strip()
            return valor if valor else defecto
        except:
            return defecto

    def _seccion(self, parent, texto):
        """Crea un label de sección"""
        tk.Label(
            parent,
            text=texto,
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0",
            fg="#333"
        ).pack(anchor='w', padx=20, pady=(12, 2))

    def _radio_si_no(self, parent, variable):
        """Crea par de radiobuttons Sí/No"""
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion, label in [('si', 'Sí'), ('no', 'No')]:
            tk.Radiobutton(
                frame, text=label,
                variable=variable, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

    def _radio_navegador(self, parent, variable):
        """Crea par de radiobuttons Firefox/Chrome"""
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['firefox', 'chrome']:
            tk.Radiobutton(
                frame, text=opcion.capitalize(),
                variable=variable, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

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

        # ==================== PESTAÑA FACEBOOK ====================
        tab_fb = ttk.Frame(notebook)
        notebook.add(tab_fb, text="📘 Facebook")

        tk.Label(tab_fb, text="Configuración para publicar mensajes bíblicos en Facebook automáticamente",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_fb, "🌐 Navegador para publicar en Facebook")
        self.var_nav_facebook = tk.StringVar(value=self._get('GENERAL', 'navegador', 'firefox'))
        self._radio_navegador(tab_fb, self.var_nav_facebook)

        self._seccion(tab_fb, "⏱️ Tiempo entre intentos (segundos)")
        self.var_tiempo_intentos = tk.StringVar(value=self._get('PUBLICACION', 'tiempo_entre_intentos', '3'))
        tk.Spinbox(tab_fb, from_=1, to=30, textvariable=self.var_tiempo_intentos, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_fb, "🔄 Máximo de intentos por publicación")
        self.var_max_intentos = tk.StringVar(value=self._get('PUBLICACION', 'max_intentos_por_publicacion', '3'))
        tk.Spinbox(tab_fb, from_=1, to=10, textvariable=self.var_max_intentos, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_fb, "⏳ Espera después de publicar (segundos)")
        self.var_espera = tk.StringVar(value=self._get('PUBLICACION', 'espera_despues_publicar', '5'))
        tk.Spinbox(tab_fb, from_=1, to=30, textvariable=self.var_espera, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        # ==================== PESTAÑA MENSAJES ====================
        tab_mensajes = ttk.Frame(notebook)
        notebook.add(tab_mensajes, text="📝 Mensajes")

        tk.Label(tab_mensajes, text="Configura cómo se eligen y formatean los mensajes bíblicos al publicar",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_mensajes, "🎲 Método de selección de mensajes")
        sel_valor = self._get('MENSAJES', 'seleccion', 'aleatorio')
        if sel_valor not in ['aleatorio', 'secuencial']:
            sel_valor = 'aleatorio'
        self.var_seleccion = tk.StringVar(value=sel_valor)
        frame_sel = tk.Frame(tab_mensajes, bg="#f0f0f0")
        frame_sel.pack(anchor='w', padx=20, pady=(0, 12))
        for opcion in ['aleatorio', 'secuencial']:
            tk.Radiobutton(
                frame_sel, text=opcion.capitalize(),
                variable=self.var_seleccion, value=opcion,
                bg="#f0f0f0", font=("Segoe UI", 10)
            ).pack(side='left', padx=8)

        self._seccion(tab_mensajes, "🧠 Memoria: últimos N mensajes a evitar repetir")
        self.var_historial = tk.StringVar(value=self._get('MENSAJES', 'historial_evitar_repetir', '5'))
        tk.Spinbox(tab_mensajes, from_=0, to=20, textvariable=self.var_historial, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_mensajes, "# Agregar hashtags automáticamente")
        self.var_hashtags = tk.StringVar(value=self._get('MENSAJES', 'agregar_hashtags', 'no'))
        self._radio_si_no(tab_mensajes, self.var_hashtags)

        self._seccion(tab_mensajes, "📎 Hashtags (separados por comas)")
        self.var_hashtags_texto = tk.StringVar(value=self._get('MENSAJES', 'hashtags', '#Fe,#Biblia'))
        tk.Entry(tab_mensajes, textvariable=self.var_hashtags_texto, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_mensajes, "🔄 Alternar mensajes bíblicos con predicaciones extraídas")
        tk.Label(tab_mensajes, text="Sí = publica 1 bíblico, 1 predicación, 1 bíblico...",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_alternar = tk.StringVar(value=self._get('PREDICACIONES', 'alternar_con_predicaciones', 'no'))
        self._radio_si_no(tab_mensajes, self.var_alternar)

        # ==================== PESTAÑA PREDICACIONES ====================
        tab_pred = ttk.Frame(notebook)
        notebook.add(tab_pred, text="🎬 Predicaciones")

        tk.Label(tab_pred,
                 text="Configuración para extraer predicaciones de un grupo de WhatsApp",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_pred, "👥 Nombre del grupo de WhatsApp (ORIGEN de predicaciones)")
        tk.Label(tab_pred, text="⚠️  Debe ser EXACTAMENTE igual a como aparece en WhatsApp",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_grupo_predicaciones = tk.StringVar(value=self._get('PREDICACIONES', 'nombre_grupo_whatsapp', ''))
        tk.Entry(tab_pred, textvariable=self.var_grupo_predicaciones, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pred, "📦 Predicaciones a extraer por vez")
        self.var_mensajes_extraccion = tk.StringVar(value=self._get('PREDICACIONES', 'mensajes_por_extraccion', '10'))
        tk.Spinbox(tab_pred, from_=1, to=50, textvariable=self.var_mensajes_extraccion, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pred, "🌐 Navegador para extracción de predicaciones")
        self.var_nav_predicaciones = tk.StringVar(value=self._get('PREDICACIONES', 'navegador', 'firefox'))
        self._radio_navegador(tab_pred, self.var_nav_predicaciones)

        # ==================== PESTAÑA ORACIONES ====================
        tab_ora = ttk.Frame(notebook)
        notebook.add(tab_ora, text="📱 Oraciones")

        tk.Label(tab_ora,
                 text="Configuración para enviar llamados de oración a grupos/contactos de WhatsApp",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_ora, "🌐 Navegador para envío de oraciones")
        self.var_nav_oraciones = tk.StringVar(value=self._get('ORACIONES', 'navegador', 'firefox'))
        self._radio_navegador(tab_ora, self.var_nav_oraciones)

        frame_info = tk.Frame(tab_ora, bg="#e8f4fd", relief='solid', borderwidth=1)
        frame_info.pack(fill='x', padx=20, pady=(15, 0))
        tk.Label(frame_info,
                 text="ℹ️  Los grupos y contactos a los que se envían oraciones\n"
                      "se configuran en el archivo:\n"
                      "llamados-oracion/grupos.json",
                 font=("Segoe UI", 9),
                 bg="#e8f4fd",
                 fg="#1a73e8",
                 justify='left').pack(padx=15, pady=10, anchor='w')

        # ==================== PESTAÑA AVANZADO ====================
        tab_adv = ttk.Frame(notebook)
        notebook.add(tab_adv, text="⚙️ Avanzado")

        tk.Label(tab_adv, text="Ajustes del navegador y límites de seguridad para evitar bloqueos",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        self._seccion(tab_adv, "👤 Usar perfil existente del navegador")
        tk.Label(tab_adv, text="Sí = usa tu sesión de Facebook/WhatsApp guardada",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_usar_perfil = tk.StringVar(value=self._get('NAVEGADOR', 'usar_perfil_existente', 'si'))
        self._radio_si_no(tab_adv, self.var_usar_perfil)

        self._seccion(tab_adv, "🖥️ Maximizar ventana al iniciar")
        self.var_maximizar = tk.StringVar(value=self._get('NAVEGADOR', 'maximizar_ventana', 'si'))
        self._radio_si_no(tab_adv, self.var_maximizar)

        self._seccion(tab_adv, "⏰ Tiempo mínimo entre publicaciones (segundos)")
        tk.Label(tab_adv, text="Evita duplicados si se ejecuta 2 veces seguidas",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_tiempo_minimo = tk.StringVar(value=self._get('LIMITES', 'tiempo_minimo_entre_publicaciones_segundos', '120'))
        tk.Spinbox(tab_adv, from_=30, to=600, textvariable=self.var_tiempo_minimo, width=8, font=("Segoe UI", 10)).pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_adv, "🔓 Permitir forzar publicación manual")
        tk.Label(tab_adv, text="Sí = permite saltarse el tiempo mínimo en ejecución manual",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_forzar_manual = tk.StringVar(value=self._get('LIMITES', 'permitir_forzar_publicacion_manual', 'si'))
        self._radio_si_no(tab_adv, self.var_forzar_manual)

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

    def ejecutar(self):
        """Inicia la interfaz gráfica"""
        self.root.mainloop()


def main():
    app = ConfiguradorGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()