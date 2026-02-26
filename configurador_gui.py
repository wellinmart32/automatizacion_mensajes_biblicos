import os
import sys
import json
import configparser
import tkinter as tk
from tkinter import ttk, messagebox


class ConfiguradorGUI:
    """Interfaz gráfica para configurar el sistema de Mensajes Bíblicos"""

    def __init__(self):
        # Leer pestaña inicial desde argumento si viene del panel
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument('--pestana', default=None)
        args, _ = parser.parse_known_args()
        self.pestana_inicial = args.pestana

        self.archivo_config = "config_global.txt"
        self.config = configparser.ConfigParser()
        self.cambios = {}

        # Ruta base siempre relativa al ejecutable
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.archivo_config = os.path.join(self.base_dir, "config_global.txt")
        self.archivo_grupos = os.path.join(self.base_dir, "llamados-oracion", "grupos.json")

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
        self.es_full = self._verificar_licencia_full()
        self._construir_ui()

    def _verificar_licencia_full(self):
        """Verifica si la licencia es FULL/MASTER desde caché o código guardado"""
        try:
            from gestor_licencias import GestorLicencias
            gl = GestorLicencias()
            codigo = gl.obtener_codigo_guardado()
            if not codigo:
                cache = gl._obtener_cache_local()
                if cache and cache.get('valida'):
                    tipo = cache.get('tipo', 'TRIAL')
                    return tipo in ['FULL', 'MASTER'] or cache.get('es_developer_permanente', False)
                return False
            resultado = gl.verificar_licencia(codigo, mostrar_mensajes=False)
            return resultado.get('valida') and (resultado.get('tipo') == 'FULL' or resultado.get('developer_permanente'))
        except Exception:
            return False

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

            # Predicaciones — solo si es FULL
            if self.es_full:
                if not self.config.has_section('PREDICACIONES'):
                    self.config.add_section('PREDICACIONES')
                self.config['PREDICACIONES']['activar_predicaciones'] = 'si'
                self.config['PREDICACIONES']['nombre_grupo_whatsapp'] = self.var_grupo_predicaciones.get()
                self.config['PREDICACIONES']['mensajes_por_extraccion'] = self.var_mensajes_extraccion.get()
                self.config['PREDICACIONES']['alternar_con_predicaciones'] = self.var_alternar.get()
                self.config['PREDICACIONES']['navegador'] = self.var_nav_predicaciones.get()

            # Oraciones — solo si es FULL
            if self.es_full:
                if not self.config.has_section('ORACIONES'):
                    self.config.add_section('ORACIONES')
                self.config['ORACIONES']['navegador'] = self.var_nav_oraciones.get()
                # Crear mensajes_oracion.txt con ejemplo si no existe
                carpeta_oraciones = os.path.join(self.base_dir, 'llamados-oracion')
                archivo_oraciones = os.path.join(carpeta_oraciones, 'mensajes_oracion.txt')
                if not os.path.exists(archivo_oraciones):
                    os.makedirs(carpeta_oraciones, exist_ok=True)
                    with open(archivo_oraciones, 'w', encoding='utf-8') as f:
                        f.write("🙏 Te invitamos a un momento de oración.\n\nDios te bendiga.")

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

        if not self.es_full:
            banner_pred = tk.Frame(tab_pred, bg="#fff3cd", pady=6)
            banner_pred.pack(fill='x', padx=20, pady=(8, 0))
            tk.Label(banner_pred, text="🔒 Estas funciones están disponibles en la versión Completa",
                     font=("Segoe UI", 9, "bold"), fg="#856404", bg="#fff3cd").pack()

        self._seccion(tab_pred, "👥 Nombre del grupo de WhatsApp (ORIGEN de predicaciones)")
        tk.Label(tab_pred, text="⚠️  Debe ser EXACTAMENTE igual a como aparece en WhatsApp",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        self.var_grupo_predicaciones = tk.StringVar(value=self._get('PREDICACIONES', 'nombre_grupo_whatsapp', ''))
        tk.Entry(tab_pred, textvariable=self.var_grupo_predicaciones, width=40, font=("Segoe UI", 10),
                 state='normal' if self.es_full else 'disabled').pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pred, "📦 Predicaciones a extraer por vez")
        self.var_mensajes_extraccion = tk.StringVar(value=self._get('PREDICACIONES', 'mensajes_por_extraccion', '10'))
        tk.Spinbox(tab_pred, from_=1, to=50, textvariable=self.var_mensajes_extraccion, width=8,
                   font=("Segoe UI", 10), state='normal' if self.es_full else 'disabled').pack(anchor='w', padx=20, pady=(0, 12))

        self._seccion(tab_pred, "🌐 Navegador para extracción de predicaciones")
        self.var_nav_predicaciones = tk.StringVar(value=self._get('PREDICACIONES', 'navegador', 'firefox'))
        frame_nav_pred = tk.Frame(tab_pred, bg="#f0f0f0")
        frame_nav_pred.pack(anchor='w', padx=20)
        for val, lbl in [('firefox', 'Firefox'), ('chrome', 'Chrome')]:
            tk.Radiobutton(frame_nav_pred, text=lbl, variable=self.var_nav_predicaciones,
                           value=val, bg="#f0f0f0", font=("Segoe UI", 10),
                           state='normal' if self.es_full else 'disabled').pack(side='left', padx=(0, 15))

        self._seccion(tab_pred, "🔄 Alternancia con mensajes bíblicos")
        tk.Label(tab_pred, text="Sí = alterna: 1 mensaje bíblico + 1 predicación + ...",
                 font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)
        frame_alt = tk.Frame(tab_pred, bg="#f0f0f0")
        frame_alt.pack(anchor='w', padx=20, pady=(4, 0))
        tk.Radiobutton(frame_alt, text="Sí", variable=self.var_alternar,
                       value="si", bg="#f0f0f0", font=("Segoe UI", 10),
                       state='normal' if self.es_full else 'disabled').pack(side='left', padx=(0, 15))
        tk.Radiobutton(frame_alt, text="No", variable=self.var_alternar,
                       value="no", bg="#f0f0f0", font=("Segoe UI", 10),
                       state='normal' if self.es_full else 'disabled').pack(side='left')

        # ==================== PESTAÑA ORACIONES ====================
        tab_ora = ttk.Frame(notebook)
        notebook.add(tab_ora, text="📱 Oraciones")

        tk.Label(tab_ora,
                 text="Configuración para enviar llamados de oración a grupos/contactos de WhatsApp",
                 font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

        if not self.es_full:
            banner_ora = tk.Frame(tab_ora, bg="#fff3cd", pady=6)
            banner_ora.pack(fill='x', padx=20, pady=(8, 0))
            tk.Label(banner_ora, text="🔒 Estas funciones están disponibles en la versión Completa",
                     font=("Segoe UI", 9, "bold"), fg="#856404", bg="#fff3cd").pack()

        self._seccion(tab_ora, "🌐 Navegador para envío de oraciones")
        self.var_nav_oraciones = tk.StringVar(value=self._get('ORACIONES', 'navegador', 'firefox'))
        frame_nav_ora = tk.Frame(tab_ora, bg="#f0f0f0")
        frame_nav_ora.pack(anchor='w', padx=20)
        for val, lbl in [('firefox', 'Firefox'), ('chrome', 'Chrome')]:
            rb = tk.Radiobutton(frame_nav_ora, text=lbl, variable=self.var_nav_oraciones,
                                value=val, bg="#f0f0f0", font=("Segoe UI", 10),
                                state='normal' if self.es_full else 'disabled')
            rb.pack(side='left', padx=(0, 15))

        self._seccion(tab_ora, "⚙️ Gestión de oraciones")

        frame_btns_ora = tk.Frame(tab_ora, bg="#f0f0f0")
        frame_btns_ora.pack(fill='x', padx=20, pady=(5, 5))

        tk.Button(
            frame_btns_ora,
            text="👥  Gestionar grupos y contactos" if self.es_full else "🔒  Gestionar grupos y contactos  —  versión Completa",
            font=("Segoe UI", 10, "bold") if self.es_full else ("Segoe UI", 10),
            bg="#1a73e8" if self.es_full else "#e0e0e0",
            fg="white" if self.es_full else "#9e9e9e",
            command=self._abrir_gestor_grupos if self.es_full else lambda: messagebox.showinfo(
                "🔒 Versión Completa", "Adquiere la versión Completa en automapro.com para gestionar grupos.")
        ).pack(fill='x', pady=(0, 8), ipady=6)

        tk.Button(
            frame_btns_ora,
            text="📝  Gestionar mensajes de oración" if self.es_full else "🔒  Gestionar mensajes de oración  —  versión Completa",
            font=("Segoe UI", 10, "bold") if self.es_full else ("Segoe UI", 10),
            bg="#28a745" if self.es_full else "#e0e0e0",
            fg="white" if self.es_full else "#9e9e9e",
            command=self._abrir_gestor_mensajes_oracion if self.es_full else lambda: messagebox.showinfo(
                "🔒 Versión Completa", "Adquiere la versión Completa en automapro.com para gestionar mensajes.")
        ).pack(fill='x', ipady=6)

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

        # Navegar a pestaña inicial si viene del panel
        if self.pestana_inicial == 'oraciones':
            notebook.select(3)

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

    def _abrir_gestor_grupos(self):
        """Abre ventana independiente para gestionar grupos y contactos"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("👥 Grupos y contactos - Oraciones")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#1a73e8", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="👥 Grupos y contactos para oraciones",
                 font=("Segoe UI", 12, "bold"), bg="#1a73e8", fg="white").pack()
        tk.Label(header, text="El nombre debe ser EXACTAMENTE igual a como aparece en WhatsApp",
                 font=("Segoe UI", 8), bg="#1a73e8", fg="#cce0ff").pack()

        frame = tk.Frame(ventana, bg="#f0f0f0", padx=20, pady=10)
        frame.pack(fill='both', expand=True)

        frame_lista = tk.Frame(frame, bg="#f0f0f0")
        frame_lista.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        lista = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set,
                           font=("Segoe UI", 10), height=8, bg="white",
                           relief='solid', borderwidth=1)
        lista.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=lista.yview)

        def cargar():
            lista.delete(0, tk.END)
            try:
                if os.path.exists(self.archivo_grupos):
                    with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    for g in datos.get('grupos', []):
                        icono = "👥" if g.get('tipo') == 'grupo' else "👤"
                        estado = "✅" if g.get('activo', True) else "❌"
                        lista.insert(tk.END, f"{estado} {icono} {g['nombre']} ({g.get('tipo','grupo')})")
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error cargando grupos: {e}")

        frame_btns = tk.Frame(frame, bg="#f0f0f0")
        frame_btns.pack(fill='x', pady=(8, 0))

        def agregar():
            self._agregar_grupo_en(ventana, cargar)

        def editar():
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecciona un grupo para editar")
                return
            self._editar_grupo_en(sel[0], ventana, cargar)

        def eliminar():
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecciona un grupo para eliminar")
                return
            idx = sel[0]
            try:
                with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                nombre = datos['grupos'][idx]['nombre']
                if not messagebox.askyesno("🗑️ Confirmar", f"¿Eliminar '{nombre}'?"):
                    return
                datos['grupos'].pop(idx)
                with open(self.archivo_grupos, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
                cargar()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error eliminando: {e}")

        tk.Button(frame_btns, text="+ Agregar", font=("Segoe UI", 10, "bold"),
                  bg="#1a73e8", fg="white", command=agregar, width=12).pack(side='left', padx=(0, 5), ipady=4)
        tk.Button(frame_btns, text="Editar", font=("Segoe UI", 10),
                  bg="#ffc107", command=editar, width=10).pack(side='left', padx=(0, 5), ipady=4)
        tk.Button(frame_btns, text="Eliminar", font=("Segoe UI", 10),
                  bg="#dc3545", fg="white", command=eliminar, width=10).pack(side='left', padx=(0, 5), ipady=4)
        tk.Button(frame_btns, text="Cerrar", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", command=ventana.destroy, width=10).pack(side='right', ipady=4)

        cargar()
        x = (self.root.winfo_screenwidth() // 2) - 220
        y = (self.root.winfo_screenheight() // 2) - 200
        ventana.geometry(f'440x380+{x}+{y}')
        ventana.deiconify()

    def _agregar_grupo_en(self, parent, callback_refresh):
        """Formulario agregar grupo sobre ventana dada"""
        v = tk.Toplevel(parent)
        v.withdraw()
        v.title("✚ Agregar grupo/contacto")
        v.resizable(False, False)
        v.configure(bg="#f0f0f0")
        v.transient(parent)
        v.grab_set()

        tk.Label(v, text="Nombre (igual que en WhatsApp):",
                 font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(20, 3))
        var_nombre = tk.StringVar()
        tk.Entry(v, textvariable=var_nombre, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20)

        tk.Label(v, text="Tipo:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 3))
        var_tipo = tk.StringVar(value="grupo")
        f = tk.Frame(v, bg="#f0f0f0")
        f.pack(anchor='w', padx=20)
        tk.Radiobutton(f, text="Grupo", variable=var_tipo, value="grupo", bg="#f0f0f0").pack(side='left', padx=(0, 10))
        tk.Radiobutton(f, text="Contacto", variable=var_tipo, value="contacto", bg="#f0f0f0").pack(side='left')

        def guardar():
            nombre = var_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío")
                return
            self._guardar_grupo_nuevo(nombre, var_tipo.get())
            callback_refresh()
            v.destroy()

        fb = tk.Frame(v, bg="#f0f0f0")
        fb.pack(fill='x', padx=20, pady=20)
        tk.Button(fb, text="Cancelar", font=("Segoe UI", 10), bg="#e0e0e0",
                  command=v.destroy, width=10).pack(side='left')
        tk.Button(fb, text="✚ Agregar", font=("Segoe UI", 10, "bold"),
                  bg="#1a73e8", fg="white", command=guardar, width=12).pack(side='right')

        v.geometry(f'400x260+{(v.winfo_screenwidth()//2)-200}+{(v.winfo_screenheight()//2)-130}')
        v.deiconify()

    def _editar_grupo_en(self, idx, parent, callback_refresh):
        """Formulario editar grupo sobre ventana dada"""
        try:
            with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            grupo = datos['grupos'][idx]
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error leyendo grupos: {e}")
            return

        v = tk.Toplevel(parent)
        v.withdraw()
        v.title("✏️ Editar grupo/contacto")
        v.resizable(False, False)
        v.configure(bg="#f0f0f0")
        v.transient(parent)
        v.grab_set()

        tk.Label(v, text="Nombre (igual que en WhatsApp):",
                 font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(20, 3))
        var_nombre = tk.StringVar(value=grupo.get('nombre', ''))
        tk.Entry(v, textvariable=var_nombre, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20)

        tk.Label(v, text="Tipo:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 3))
        var_tipo = tk.StringVar(value=grupo.get('tipo', 'grupo'))
        f = tk.Frame(v, bg="#f0f0f0")
        f.pack(anchor='w', padx=20)
        tk.Radiobutton(f, text="Grupo", variable=var_tipo, value="grupo", bg="#f0f0f0").pack(side='left', padx=(0, 10))
        tk.Radiobutton(f, text="Contacto", variable=var_tipo, value="contacto", bg="#f0f0f0").pack(side='left')

        def guardar():
            nombre = var_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío")
                return
            datos['grupos'][idx] = {'nombre': nombre, 'tipo': var_tipo.get(), 'activo': True}
            try:
                with open(self.archivo_grupos, 'w', encoding='utf-8') as f2:
                    json.dump(datos, f2, ensure_ascii=False, indent=2)
                callback_refresh()
                v.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error guardando: {e}")

        fb = tk.Frame(v, bg="#f0f0f0")
        fb.pack(fill='x', padx=20, pady=20)
        tk.Button(fb, text="Cancelar", font=("Segoe UI", 10), bg="#e0e0e0",
                  command=v.destroy, width=10).pack(side='left')
        tk.Button(fb, text="💾 Guardar", font=("Segoe UI", 10, "bold"),
                  bg="#1a73e8", fg="white", command=guardar, width=12).pack(side='right')

        v.geometry(f'400x260+{(v.winfo_screenwidth()//2)-200}+{(v.winfo_screenheight()//2)-130}')
        v.deiconify()

    def _abrir_gestor_mensajes_oracion(self):
        """Abre ventana independiente para gestionar mensajes de oración"""
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("📝 Mensajes de oración")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#28a745", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="📝 Mensajes de oración",
                 font=("Segoe UI", 12, "bold"), bg="#28a745", fg="white").pack()
        tk.Label(header, text="Un mensaje por línea en cada sección",
                 font=("Segoe UI", 8), bg="#28a745", fg="#ccffdd").pack()

        # Sección GRUPOS
        frame = tk.Frame(ventana, bg="#f0f0f0", padx=20, pady=10)
        frame.pack(fill='both', expand=True)

        tk.Label(frame, text="Para GRUPOS:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w')
        tk.Label(frame, text="Se envía a grupos de WhatsApp", font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w')

        frame_g = tk.Frame(frame, bg="#f0f0f0")
        frame_g.pack(fill='both', expand=True, pady=(3, 8))
        scroll_g = tk.Scrollbar(frame_g)
        scroll_g.pack(side='right', fill='y')
        lista_grupos_msg = tk.Listbox(frame_g, yscrollcommand=scroll_g.set,
                                      font=("Segoe UI", 9), height=5, bg="white",
                                      relief='solid', borderwidth=1, selectmode='single')
        lista_grupos_msg.pack(side='left', fill='both', expand=True)
        scroll_g.config(command=lista_grupos_msg.yview)

        frame_btn_g = tk.Frame(frame, bg="#f0f0f0")
        frame_btn_g.pack(fill='x', pady=(0, 10))

        # Sección INDIVIDUALES
        tk.Label(frame, text="Para INDIVIDUALES:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w')
        tk.Label(frame, text="Se envía a contactos individuales", font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w')

        frame_i = tk.Frame(frame, bg="#f0f0f0")
        frame_i.pack(fill='both', expand=True, pady=(3, 8))
        scroll_i = tk.Scrollbar(frame_i)
        scroll_i.pack(side='right', fill='y')
        lista_ind_msg = tk.Listbox(frame_i, yscrollcommand=scroll_i.set,
                                   font=("Segoe UI", 9), height=5, bg="white",
                                   relief='solid', borderwidth=1, selectmode='single')
        lista_ind_msg.pack(side='left', fill='both', expand=True)
        scroll_i.config(command=lista_ind_msg.yview)

        frame_btn_i = tk.Frame(frame, bg="#f0f0f0")
        frame_btn_i.pack(fill='x', pady=(0, 5))

        archivo_msg = os.path.join(self.base_dir, "llamados-oracion", "mensajes_oracion.txt")

        def cargar_mensajes():
            lista_grupos_msg.delete(0, tk.END)
            lista_ind_msg.delete(0, tk.END)
            if not os.path.exists(archivo_msg):
                return
            with open(archivo_msg, 'r', encoding='utf-8') as f:
                contenido = f.read()
            if '[GRUPOS]' in contenido and '[INDIVIDUALES]' in contenido:
                partes = contenido.split('[INDIVIDUALES]')
                for linea in partes[0].replace('[GRUPOS]', '').strip().split('\n'):
                    if linea.strip():
                        lista_grupos_msg.insert(tk.END, linea.strip())
                for linea in partes[1].strip().split('\n'):
                    if linea.strip():
                        lista_ind_msg.insert(tk.END, linea.strip())

        def guardar_mensajes():
            grupos = list(lista_grupos_msg.get(0, tk.END))
            inds = list(lista_ind_msg.get(0, tk.END))
            if not grupos or not inds:
                messagebox.showerror("❌ Error", "Debe haber al menos un mensaje en cada sección")
                return
            contenido = "[GRUPOS]\n" + "\n".join(grupos) + "\n\n[INDIVIDUALES]\n" + "\n".join(inds) + "\n"
            os.makedirs(os.path.dirname(archivo_msg), exist_ok=True)
            with open(archivo_msg, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo("✅ Guardado", "Mensajes de oración guardados correctamente.")

        def agregar_msg(lista):
            v = tk.Toplevel(ventana)
            v.withdraw()
            v.title("✚ Nuevo mensaje")
            v.resizable(False, False)
            v.configure(bg="#f0f0f0")
            v.transient(ventana)
            v.grab_set()
            tk.Label(v, text="Texto del mensaje:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(20, 3))
            txt = tk.Text(v, font=("Segoe UI", 10), height=4, width=45, relief='solid', borderwidth=1)
            txt.pack(padx=20)
            def confirmar():
                texto = txt.get('1.0', tk.END).strip()
                if not texto:
                    return
                lista.insert(tk.END, texto)
                v.destroy()
            fb = tk.Frame(v, bg="#f0f0f0")
            fb.pack(fill='x', padx=20, pady=15)
            tk.Button(fb, text="Cancelar", bg="#e0e0e0", font=("Segoe UI", 10),
                      command=v.destroy, width=10).pack(side='left')
            tk.Button(fb, text="✚ Agregar", bg="#1a73e8", fg="white", font=("Segoe UI", 10, "bold"),
                      command=confirmar, width=12).pack(side='right')
            v.geometry(f'420x220+{(v.winfo_screenwidth()//2)-210}+{(v.winfo_screenheight()//2)-110}')
            v.deiconify()

        def editar_msg(lista):
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecciona un mensaje para editar")
                return
            idx = sel[0]
            texto_actual = lista.get(idx)
            v = tk.Toplevel(ventana)
            v.withdraw()
            v.title("✏️ Editar mensaje")
            v.resizable(False, False)
            v.configure(bg="#f0f0f0")
            v.transient(ventana)
            v.grab_set()
            tk.Label(v, text="Texto del mensaje:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(20, 3))
            txt = tk.Text(v, font=("Segoe UI", 10), height=4, width=45, relief='solid', borderwidth=1)
            txt.insert('1.0', texto_actual)
            txt.pack(padx=20)
            def confirmar():
                texto = txt.get('1.0', tk.END).strip()
                if not texto:
                    return
                lista.delete(idx)
                lista.insert(idx, texto)
                v.destroy()
            fb = tk.Frame(v, bg="#f0f0f0")
            fb.pack(fill='x', padx=20, pady=15)
            tk.Button(fb, text="Cancelar", bg="#e0e0e0", font=("Segoe UI", 10),
                      command=v.destroy, width=10).pack(side='left')
            tk.Button(fb, text="💾 Guardar", bg="#1a73e8", fg="white", font=("Segoe UI", 10, "bold"),
                      command=confirmar, width=12).pack(side='right')
            v.geometry(f'420x220+{(v.winfo_screenwidth()//2)-210}+{(v.winfo_screenheight()//2)-110}')
            v.deiconify()

        def eliminar_msg(lista):
            sel = lista.curselection()
            if not sel:
                messagebox.showwarning("⚠️ Aviso", "Selecciona un mensaje para eliminar")
                return
            if messagebox.askyesno("🗑️ Confirmar", "¿Eliminar este mensaje?"):
                lista.delete(sel[0])

        # Botones grupos mensajes
        tk.Button(frame_btn_g, text="✚ Agregar", font=("Segoe UI", 9, "bold"),
                  bg="#1a73e8", fg="white", command=lambda: agregar_msg(lista_grupos_msg)).pack(side='left', padx=(0, 5), ipady=3)
        tk.Button(frame_btn_g, text="✏️ Editar", font=("Segoe UI", 9),
                  bg="#ffc107", command=lambda: editar_msg(lista_grupos_msg)).pack(side='left', padx=(0, 5), ipady=3)
        tk.Button(frame_btn_g, text="🗑️ Eliminar", font=("Segoe UI", 9),
                  bg="#dc3545", fg="white", command=lambda: eliminar_msg(lista_grupos_msg)).pack(side='left', ipady=3)

        # Botones individuales mensajes
        tk.Button(frame_btn_i, text="✚ Agregar", font=("Segoe UI", 9, "bold"),
                  bg="#1a73e8", fg="white", command=lambda: agregar_msg(lista_ind_msg)).pack(side='left', padx=(0, 5), ipady=3)
        tk.Button(frame_btn_i, text="✏️ Editar", font=("Segoe UI", 9),
                  bg="#ffc107", command=lambda: editar_msg(lista_ind_msg)).pack(side='left', padx=(0, 5), ipady=3)
        tk.Button(frame_btn_i, text="🗑️ Eliminar", font=("Segoe UI", 9),
                  bg="#dc3545", fg="white", command=lambda: eliminar_msg(lista_ind_msg)).pack(side='left', ipady=3)

        def cerrar_guardando():
            guardar_mensajes()
            ventana.destroy()

        # Botón cerrar (guarda automáticamente)
        frame_footer = tk.Frame(ventana, bg="#f0f0f0")
        frame_footer.pack(fill='x', padx=20, pady=(0, 15))
        tk.Button(frame_footer, text="✅ Guardar y cerrar", font=("Segoe UI", 10, "bold"),
                  bg="#28a745", fg="white", command=cerrar_guardando, width=20).pack(ipady=4)

        ventana.protocol("WM_DELETE_WINDOW", cerrar_guardando)

        cargar_mensajes()
        x = (self.root.winfo_screenwidth() // 2) - 240
        y = (self.root.winfo_screenheight() // 2) - 300
        ventana.geometry(f'480x580+{x}+{y}')
        ventana.deiconify()

    def _cargar_mensajes_oracion(self):
        """Crea mensajes_oracion.txt con plantilla si no existe"""
        archivo = os.path.join(self.base_dir, "llamados-oracion", "mensajes_oracion.txt")
        if not os.path.exists(archivo):
            os.makedirs(os.path.dirname(archivo), exist_ok=True)
            plantilla = (
                "[GRUPOS]\n"
                "Hermanos, los invitamos a orar juntos hoy. ¡Dios escucha nuestras oraciones!\n"
                "Únete a nosotros en este momento de oración y adoración.\n\n"
                "[INDIVIDUALES]\n"
                "Hola, te invito a unirte a nuestra cadena de oración hoy.\n"
                "Que Dios te bendiga hoy. Te recordamos en oración.\n"
            )
            with open(archivo, 'w', encoding='utf-8') as f:
                f.write(plantilla)

    def _cargar_grupos_lista(self):
        """Carga grupos desde grupos.json en la lista visual"""
        self.lista_grupos.delete(0, tk.END)
        if not os.path.exists(self.archivo_grupos):
            return
        try:
            with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            for g in datos.get('grupos', []):
                activo = "✅" if g.get('activo', True) else "❌"
                tipo = "👥" if g.get('tipo') == 'grupo' else "👤"
                self.lista_grupos.insert(tk.END, f"{activo} {tipo} {g['nombre']}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error leyendo grupos: {e}")

    def _agregar_grupo(self):
        """Diálogo para agregar un grupo/contacto"""
        ventana = tk.Toplevel(self.root)
        ventana.title("✚ Agregar grupo/contacto")
        ventana.geometry("400x220")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()
        ventana.withdraw()
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - 200
        y = (ventana.winfo_screenheight() // 2) - 110
        ventana.geometry(f'400x220+{x}+{y}')
        ventana.deiconify()

        tk.Label(ventana, text="Nombre (igual que en WhatsApp):",
                 font=("Segoe UI", 10), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(15, 2))
        var_nombre = tk.StringVar()
        tk.Entry(ventana, textvariable=var_nombre, width=40,
                 font=("Segoe UI", 10)).pack(padx=20, fill='x')

        tk.Label(ventana, text="Tipo:", font=("Segoe UI", 10),
                 bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 2))
        var_tipo = tk.StringVar(value='grupo')
        frame_tipo = tk.Frame(ventana, bg="#f0f0f0")
        frame_tipo.pack(anchor='w', padx=20)
        tk.Radiobutton(frame_tipo, text="👥 Grupo", variable=var_tipo,
                       value='grupo', bg="#f0f0f0").pack(side='left', padx=(0, 15))
        tk.Radiobutton(frame_tipo, text="👤 Individual", variable=var_tipo,
                       value='individual', bg="#f0f0f0").pack(side='left')

        def _confirmar():
            nombre = var_nombre.get().strip()
            if not nombre:
                messagebox.showwarning("⚠️ Aviso", "Escribe el nombre", parent=ventana)
                return
            self._guardar_grupo_nuevo(nombre, var_tipo.get())
            self._cargar_grupos_lista()
            ventana.destroy()

        tk.Button(ventana, text="✚ Agregar", font=("Segoe UI", 10, "bold"),
                  bg="#1a73e8", fg="white", command=_confirmar).pack(pady=15)

    def _guardar_grupo_nuevo(self, nombre, tipo):
        """Agrega un grupo al JSON"""
        datos = {"grupos": []}
        if os.path.exists(self.archivo_grupos):
            try:
                with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
            except:
                pass
        datos['grupos'].append({"nombre": nombre, "tipo": tipo, "activo": True, "descripcion": ""})
        os.makedirs(os.path.dirname(self.archivo_grupos), exist_ok=True)
        with open(self.archivo_grupos, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

    def _eliminar_grupo(self):
        """Elimina el grupo seleccionado del JSON"""
        seleccion = self.lista_grupos.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un grupo para eliminar")
            return
        idx = seleccion[0]
        try:
            with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            nombre = datos['grupos'][idx]['nombre']
            if not messagebox.askyesno("🗑️ Confirmar", f"¿Eliminar '{nombre}'?"):
                return
            datos['grupos'].pop(idx)
            with open(self.archivo_grupos, 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
            self._cargar_grupos_lista()
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error eliminando grupo: {e}")

    def _editar_grupo(self):
        """Edita el grupo/contacto seleccionado"""
        seleccion = self.lista_grupos.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un grupo para editar")
            return
        idx = seleccion[0]
        try:
            with open(self.archivo_grupos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            grupo = datos['grupos'][idx]
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error leyendo grupos: {e}")
            return

        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("✏️ Editar grupo/contacto")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        tk.Label(ventana, text="Nombre (igual que en WhatsApp):",
                 font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(20, 3))
        var_nombre = tk.StringVar(value=grupo.get('nombre', ''))
        tk.Entry(ventana, textvariable=var_nombre, width=40, font=("Segoe UI", 10)).pack(anchor='w', padx=20)

        tk.Label(ventana, text="Tipo:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 3))
        var_tipo = tk.StringVar(value=grupo.get('tipo', 'grupo'))
        frame_tipo = tk.Frame(ventana, bg="#f0f0f0")
        frame_tipo.pack(anchor='w', padx=20)
        tk.Radiobutton(frame_tipo, text="Grupo", variable=var_tipo, value="grupo", bg="#f0f0f0").pack(side='left', padx=(0, 10))
        tk.Radiobutton(frame_tipo, text="Contacto", variable=var_tipo, value="contacto", bg="#f0f0f0").pack(side='left')

        frame_btns = tk.Frame(ventana, bg="#f0f0f0")
        frame_btns.pack(fill='x', pady=20, padx=20)

        def guardar():
            nombre = var_nombre.get().strip()
            if not nombre:
                messagebox.showerror("Error", "El nombre no puede estar vacío")
                return
            datos['grupos'][idx] = {'nombre': nombre, 'tipo': var_tipo.get()}
            try:
                with open(self.archivo_grupos, 'w', encoding='utf-8') as f:
                    json.dump(datos, f, ensure_ascii=False, indent=2)
                self._cargar_grupos_lista()
                ventana.destroy()
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error guardando: {e}")

        tk.Button(frame_btns, text="Cancelar", font=("Segoe UI", 10), bg="#e0e0e0",
                  command=ventana.destroy, width=10).pack(side='left')
        tk.Button(frame_btns, text="💾 Guardar", font=("Segoe UI", 10, "bold"),
                  bg="#1a73e8", fg="white", command=guardar, width=12).pack(side='right')

        x = (ventana.winfo_screenwidth() // 2) - 200
        y = (ventana.winfo_screenheight() // 2) - 150
        ventana.geometry(f'400x300+{x}+{y}')
        ventana.deiconify()

    def ejecutar(self):
        """Inicia la interfaz gráfica"""
        self.root.mainloop()


def main():
    app = ConfiguradorGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()