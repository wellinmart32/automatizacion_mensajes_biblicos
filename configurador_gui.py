import os
import sys
import json
import configparser
import tkinter as tk
from tkinter import ttk, messagebox


class ConfiguradorGUI:
    """Interfaz gráfica para configurar el sistema de Mensajes Bíblicos"""

    def __init__(self):
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
                self.config['PREDICACIONES']['nombre_grupo_whatsapp'] = self.var_grupo_predicaciones.get()
                self.config['PREDICACIONES']['mensajes_por_extraccion'] = self.var_mensajes_extraccion.get()
                self.config['PREDICACIONES']['alternar_con_predicaciones'] = self.var_alternar.get()
                self.config['PREDICACIONES']['navegador'] = self.var_nav_predicaciones.get()

            # Oraciones — solo si es FULL
            if self.es_full:
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

        if not self.es_full:
            tk.Label(tab_pred, text="🔒 Función disponible en versión Completa",
                     font=("Segoe UI", 12, "bold"), fg="#dc3545", bg="#f0f0f0").pack(pady=(30, 5))
            tk.Label(tab_pred, text="Extrae y publica predicaciones automáticamente desde WhatsApp.\nAdquiere la versión Completa en automapro.com",
                     font=("Segoe UI", 10), fg="#555", bg="#f0f0f0", justify='center').pack(pady=5)
            tk.Button(tab_pred, text="⬆️ Ver planes", font=("Segoe UI", 10, "bold"),
                      bg="#1a73e8", fg="white", command=lambda: messagebox.showinfo("Versión Completa", "Visita automapro.com para adquirir la versión Completa.")).pack(pady=15)
        else:
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

        if not self.es_full:
            tk.Label(tab_ora, text="🔒 Función disponible en versión Completa",
                     font=("Segoe UI", 12, "bold"), fg="#dc3545", bg="#f0f0f0").pack(pady=(30, 5))
            tk.Label(tab_ora, text="Envía llamados de oración automáticamente a grupos y contactos de WhatsApp.\nAdquiere la versión Completa en automapro.com",
                     font=("Segoe UI", 10), fg="#555", bg="#f0f0f0", justify='center').pack(pady=5)
            tk.Button(tab_ora, text="⬆️ Ver planes", font=("Segoe UI", 10, "bold"),
                      bg="#1a73e8", fg="white", command=lambda: messagebox.showinfo("Versión Completa", "Visita automapro.com para adquirir la versión Completa.")).pack(pady=15)
        else:
            tk.Label(tab_ora,
                     text="Configuración para enviar llamados de oración a grupos/contactos de WhatsApp",
                     font=("Segoe UI", 9), fg="#555", bg="#f0f0f0").pack(anchor='w', padx=20, pady=(10, 0))

            self._seccion(tab_ora, "🌐 Navegador para envío de oraciones")
            self.var_nav_oraciones = tk.StringVar(value=self._get('ORACIONES', 'navegador', 'firefox'))
            self._radio_navegador(tab_ora, self.var_nav_oraciones)

            self._seccion(tab_ora, "👥 Grupos y contactos a los que se envían oraciones")
            tk.Label(tab_ora, text="El nombre debe ser EXACTAMENTE igual a como aparece en WhatsApp",
                     font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w', padx=20)

            frame_grupos = tk.Frame(tab_ora, bg="#f0f0f0")
            frame_grupos.pack(fill='both', expand=True, padx=20, pady=(5, 0))

            frame_lista_g = tk.Frame(frame_grupos, bg="#f0f0f0")
            frame_lista_g.pack(fill='both', expand=True)

            scrollbar_g = tk.Scrollbar(frame_lista_g)
            scrollbar_g.pack(side='right', fill='y')

            self.lista_grupos = tk.Listbox(
                frame_lista_g,
                yscrollcommand=scrollbar_g.set,
                font=("Segoe UI", 9),
                height=5,
                bg="white",
                relief='solid',
                borderwidth=1
            )
            self.lista_grupos.pack(side='left', fill='both', expand=True)
            scrollbar_g.config(command=self.lista_grupos.yview)

            frame_btn_g = tk.Frame(tab_ora, bg="#f0f0f0")
            frame_btn_g.pack(fill='x', padx=20, pady=(5, 0))

            tk.Button(frame_btn_g, text="✚ Agregar",
                      font=("Segoe UI", 9, "bold"), bg="#1a73e8", fg="white",
                      command=self._agregar_grupo).pack(side='left', padx=(0, 5))
            tk.Button(frame_btn_g, text="✏️ Editar",
                      font=("Segoe UI", 9), bg="#ffc107",
                      command=self._editar_grupo).pack(side='left', padx=(0, 5))
            tk.Button(frame_btn_g, text="🗑️ Eliminar",
                      font=("Segoe UI", 9), bg="#dc3545", fg="white",
                      command=self._eliminar_grupo).pack(side='left')

            self._cargar_grupos_lista()

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