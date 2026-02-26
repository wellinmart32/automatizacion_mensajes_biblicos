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

        # Ruta base del ejecutable
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

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

        self._botones_grid = []  # Para bloquear/desbloquear todos juntos

        # Fila 0
        self._boton(grid, "⚡\nAcciones", "Publicar y automatizar",
                    self._abrir_acciones, row=0, col=0, color="#e65100")
        self._boton(grid, "⚙️\nConfigurador", "Ajustar configuración",
                    self._abrir_configurador, row=0, col=1, en_hilo=True)

        # Fila 1
        if es_full:
            self._boton(grid, "📝\nMensajes", "Crear y editar mensajes",
                        self._abrir_gestor_mensajes, row=1, col=0, en_hilo=True)
        else:
            self._boton(grid, "📝\nMensajes", "Ver tus mensajes",
                        self._abrir_carpeta_mensajes, row=1, col=0)
        self._boton(grid, "📊\nEstadísticas", "Ver historial",
                    self._ver_estadisticas, row=1, col=1)

        # Fila 2
        if es_full:
            self._boton(grid, "🗓️\nTareas Automáticas", "Programar publicaciones",
                        self._gestionar_tareas, row=2, col=0, color="#28a745", en_hilo=True)
        else:
            self._boton(grid, "🔒\nTareas Automáticas", "Solo versión Completa",
                        self._mostrar_mensaje_upgrade, row=2, col=0, color="#9e9e9e")

        self._boton(grid, "❓\nAyuda", "Cómo usar el sistema",
                    self._mostrar_ayuda, row=2, col=1)

        # Fila 3
        self._boton(grid, "❌\nSalir", "Cerrar panel",
                    self.root.destroy, row=3, col=0, color="#dc3545")

    def _bloquear_grid(self):
        """Bloquea todos los botones del grid"""
        self.root.config(cursor="wait")
        for frame, widgets in self._botones_grid:
            frame.config(cursor="", bg="#e0e0e0")
            for w in widgets:
                w.config(bg="#e0e0e0")
                w.unbind('<Button-1>')
                w.unbind('<Enter>')
                w.unbind('<Leave>')
            frame.unbind('<Button-1>')
            frame.unbind('<Enter>')
            frame.unbind('<Leave>')

    def _desbloquear_grid(self):
        """Restaura todos los botones del grid"""
        self.root.config(cursor="")
        for frame, widgets in self._botones_grid:
            frame.config(cursor="hand2", bg="white")
            cmd = frame._cmd
            en_hilo = frame._en_hilo
            for w in widgets:
                w.config(bg="white")
                accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd
                w.bind('<Button-1>', lambda e, a=accion: a())
                w.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
                w.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))
            accion = (lambda c=cmd: self._lanzar_en_hilo(c)) if en_hilo else cmd
            frame.bind('<Button-1>', lambda e, a=accion: a())
            frame.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
            frame.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))

    def _lanzar_accion(self, cmd):
        """Para acciones que abren ventanas: bloquea grid brevemente para evitar doble clic"""
        self._bloquear_grid()
        self.root.after(300, self._desbloquear_grid)
        cmd()

    def _lanzar_en_hilo(self, cmd):
        """Para subprocesos: bloquea grid, corre en hilo, desbloquea al terminar"""
        self._bloquear_grid()
        import threading
        def _hilo():
            try:
                cmd()
            finally:
                self.root.after(0, self._desbloquear_grid)
        threading.Thread(target=_hilo, daemon=True).start()

    def _centrar_ventana(self, ventana, ancho, alto):
        """Centra una ventana en pantalla antes de mostrarla"""
        x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana.winfo_screenheight() // 2) - (alto // 2)
        ventana.geometry(f'{ancho}x{alto}+{x}+{y}')

    def _boton(self, parent, texto, subtexto, comando, row, col, color="#1a73e8", en_hilo=False):
        """Crea un botón estilizado en el grid"""
        frame = tk.Frame(parent, bg="white", relief='solid', borderwidth=1, cursor="hand2")
        frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)
        frame._cmd = comando
        frame._en_hilo = en_hilo

        lbl1 = tk.Label(frame, text=texto, font=("Segoe UI", 13, "bold"), bg="white", fg=color)
        lbl1.pack(expand=True, pady=(12, 3))

        lbl2 = tk.Label(frame, text=subtexto, font=("Segoe UI", 8), bg="white", fg="gray")
        lbl2.pack(expand=True, pady=(0, 12))

        if en_hilo:
            accion = lambda c=comando: self._lanzar_en_hilo(c)
        else:
            accion = lambda c=comando: self._lanzar_accion(c)
        for w in [frame, lbl1, lbl2]:
            w.bind('<Button-1>', lambda e, a=accion: a())
            w.bind('<Enter>', lambda e, f=frame: f.config(bg="#f8f9fa"))
            w.bind('<Leave>', lambda e, f=frame: f.config(bg="white"))

        self._botones_grid.append((frame, [lbl1, lbl2]))

    # ==================== VENTANA ACCIONES ====================

    def _abrir_acciones(self):
        """Abre ventana de acciones disponibles según licencia"""
        tipo_licencia = self.licencia.get('tipo', 'TRIAL')
        es_full = tipo_licencia in ['FULL', 'MASTER'] or self.licencia.get('developer_permanente')

        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("⚡ Acciones")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

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

        # Verificar predicaciones pendientes desde archivo de estado
        from compartido.gestor_archivos import leer_estado_predicaciones
        estado = leer_estado_predicaciones()
        hay_predicaciones = estado.get('pendientes', 0) > 0

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
        tk.Button(
            frame,
            text="📱  Enviar Oraciones por WhatsApp" if es_full else "🔒  Enviar Oraciones por WhatsApp  —  versión Completa",
            font=("Segoe UI", 11, "bold") if es_full else ("Segoe UI", 11),
            bg="#25D366" if es_full else "#e0e0e0",
            fg="white" if es_full else "#9e9e9e",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=lambda: [ventana.destroy(), self._enviar_oraciones()] if es_full else self._mostrar_mensaje_upgrade()
        ).pack(fill='x', pady=(0, 8))

        # Acción 3 — Extraer Predicaciones de WhatsApp
        tk.Button(
            frame,
            text="🎬  Extraer Predicaciones de WhatsApp" if es_full else "🔒  Extraer Predicaciones de WhatsApp  —  versión Completa",
            font=("Segoe UI", 11, "bold") if es_full else ("Segoe UI", 11),
            bg="#25D366" if es_full else "#e0e0e0",
            fg="white" if es_full else "#9e9e9e",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=lambda: [ventana.destroy(), self._extraer_predicaciones()] if es_full else self._mostrar_mensaje_upgrade()
        ).pack(fill='x', pady=(0, 8))

        # Acción 4 — Publicar Predicaciones en Facebook
        if es_full:
            color_pred = "#1a73e8" if hay_predicaciones else "#90a4ae"
            cmd_pred = (lambda: [ventana.destroy(), self._publicar_predicaciones()]) \
                       if hay_predicaciones else self._sin_predicaciones
            texto_pred = "📤  Publicar Prédica Extraída" if hay_predicaciones else "📭  Sin prédicas extraídas"
        else:
            color_pred = "#e0e0e0"
            cmd_pred = self._mostrar_mensaje_upgrade
            texto_pred = "🔒  Publicar Prédica Extraída  —  versión Completa"
        tk.Button(
            frame,
            text=texto_pred,
            font=("Segoe UI", 11, "bold") if es_full else ("Segoe UI", 11),
            bg=color_pred,
            fg="white" if es_full else "#9e9e9e",
            cursor="hand2",
            anchor='w',
            padx=15,
            pady=8,
            command=cmd_pred
        ).pack(fill='x', pady=(0, 8))

        tk.Button(
            frame,
            text="Cerrar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            width=12,
            command=ventana.destroy
        ).pack(pady=15)

        self._centrar_ventana(ventana, 500, 420)
        ventana.deiconify()

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
        """Muestra diálogo de selección de grupos antes de enviar"""
        import json

        archivo_grupos = os.path.join(self.base_dir, "llamados-oracion", "grupos.json")
        grupos_vacios = False

        if not os.path.exists(archivo_grupos):
            grupos_vacios = True
        else:
            try:
                with open(archivo_grupos, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                grupos = [g for g in datos.get('grupos', []) if g.get('activo', True)]
                if not grupos:
                    grupos_vacios = True
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error leyendo grupos:\n{e}")
                return

        if grupos_vacios:
            respuesta = messagebox.askokcancel(
                "⚠️ Sin grupos configurados",
                "No hay grupos de oración configurados.\n\n"
                "¿Deseas abrir el Configurador para agregarlos ahora?"
            )
            if respuesta:
                self._abrir_configurador(pestaña='oraciones')
            return

        # Diálogo de selección
        ventana = tk.Toplevel(self.root)
        ventana.withdraw()
        ventana.title("📱 Seleccionar destinatarios")
        ventana.resizable(False, False)
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()

        header = tk.Frame(ventana, bg="#25D366", pady=12)
        header.pack(fill='x')
        tk.Label(header, text="📱 Enviar llamados de oración",
                 font=("Segoe UI", 12, "bold"), bg="#25D366", fg="white").pack()
        tk.Label(header, text="Selecciona a quiénes enviar hoy",
                 font=("Segoe UI", 9), bg="#25D366", fg="#d0f5e0").pack()

        frame = tk.Frame(ventana, bg="#f0f0f0", padx=20, pady=10)
        frame.pack(fill='both', expand=True)

        # Checkbox seleccionar todos
        var_todos = tk.BooleanVar(value=True)
        vars_grupos = []

        def toggle_todos():
            for v in vars_grupos:
                v.set(var_todos.get())

        chk_todos = tk.Checkbutton(frame, text="✅ Seleccionar todos",
                                   variable=var_todos, command=toggle_todos,
                                   font=("Segoe UI", 10, "bold"), bg="#f0f0f0")
        chk_todos.pack(anchor='w', pady=(0, 5))

        tk.Frame(frame, bg="#ccc", height=1).pack(fill='x', pady=(0, 8))

        # Checkboxes individuales
        frame_scroll = tk.Frame(frame, bg="#f0f0f0")
        frame_scroll.pack(fill='both', expand=True)

        for g in grupos:
            var = tk.BooleanVar(value=True)
            vars_grupos.append(var)
            icono = "👥" if g.get('tipo') == 'grupo' else "👤"
            tk.Checkbutton(frame_scroll,
                           text=f"{icono} {g['nombre']} ({g.get('tipo','grupo')})",
                           variable=var, bg="#f0f0f0",
                           font=("Segoe UI", 10)).pack(anchor='w', pady=2)

        def actualizar_todos(*args):
            todos_marcados = all(v.get() for v in vars_grupos)
            var_todos.set(todos_marcados)

        for v in vars_grupos:
            v.trace_add('write', actualizar_todos)

        # Botones
        frame_btns = tk.Frame(ventana, bg="#f0f0f0", padx=20)
        frame_btns.pack(fill='x', pady=(5, 15))

        def cancelar():
            ventana.destroy()

        def confirmar():
            seleccionados = [grupos[i] for i, v in enumerate(vars_grupos) if v.get()]
            if not seleccionados:
                messagebox.showwarning("⚠️ Aviso", "Selecciona al menos un destinatario.")
                return

            # Escribir selección temporal
            temp_file = os.path.join(self.base_dir, "llamados-oracion", "seleccion_temp.json")
            try:
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump({"grupos": seleccionados}, f, ensure_ascii=False, indent=2)
            except Exception as e:
                messagebox.showerror("❌ Error", f"Error preparando selección:\n{e}")
                return

            ventana.destroy()
            try:
                exe = self._exe("OracionesWhatsApp.exe")
                if os.path.exists(exe):
                    subprocess.Popen([exe])
                else:
                    subprocess.Popen([sys.executable,
                                      os.path.join("publicadores", "whatsapp_oracion.py")])
                self._toast("📱 Oraciones WhatsApp",
                            f"Enviando a {len(seleccionados)} destinatario(s)...")
            except Exception as e:
                messagebox.showerror("❌ Error", f"No se pudo iniciar el módulo:\n{e}")

        tk.Button(frame_btns, text="Cancelar", font=("Segoe UI", 10),
                  bg="#6c757d", fg="white", command=cancelar, width=10).pack(side='left', ipady=4)
        tk.Button(frame_btns, text="📱 Enviar ahora", font=("Segoe UI", 10, "bold"),
                  bg="#25D366", fg="white", command=confirmar, width=16).pack(side='right', ipady=4)

        self._centrar_ventana(ventana, 420, min(120 + len(grupos) * 35 + 80, 500))
        ventana.deiconify()

    def _abrir_configurador(self, pestaña=None):
        """Abre el configurador — deshabilita el botón mientras está abierto"""
        try:
            exe = self._exe("ConfiguradorMensajes.exe")
            args = [exe] if os.path.exists(exe) else [sys.executable, "configurador_gui.py"]
            if pestaña:
                args.append(f"--pestana={pestaña}")

            # Deshabilitar botón configurador mientras está abierto
            for widget in self.root.winfo_children():
                try:
                    if hasattr(widget, 'winfo_children'):
                        for child in widget.winfo_children():
                            if hasattr(child, 'cget') and 'Configurador' in str(child.cget('text') if hasattr(child, 'cget') else ''):
                                child.config(state='disabled')
                except:
                    pass

            proceso = subprocess.Popen(args)
            self._toast("⚙️ Configurador", "Abriendo configurador...")

            def _esperar_cierre():
                proceso.wait()
                self.root.after(0, self._rehabilitar_botones)

            import threading
            threading.Thread(target=_esperar_cierre, daemon=True).start()

        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el configurador:\n{e}")

    def _rehabilitar_botones(self):
        """Rehabilita todos los botones del panel tras cerrar subventana"""
        try:
            for widget in self.root.winfo_children():
                if hasattr(widget, 'winfo_children'):
                    for child in widget.winfo_children():
                        try:
                            child.config(state='normal')
                        except:
                            pass
        except:
            pass

    def _extraer_predicaciones(self):
        # Verificar si el grupo está configurado antes de lanzar el exe
        archivo_config = os.path.join(self.base_dir, "config_global.txt")
        import configparser as _cp
        cfg = _cp.ConfigParser()
        cfg.read(archivo_config, encoding='utf-8')
        nombre_actual = cfg.get('PREDICACIONES', 'nombre_grupo_whatsapp', fallback='Prédicas').strip()

        VALORES_DEFAULT = {''}
        if nombre_actual in VALORES_DEFAULT:
            ventana = tk.Toplevel(self.root)
            ventana.withdraw()
            ventana.title("📱 Configurar grupo de WhatsApp")
            ventana.resizable(False, False)
            ventana.configure(bg="#f0f0f0")
            ventana.transient(self.root)
            ventana.grab_set()

            header = tk.Frame(ventana, bg="#25D366", pady=12)
            header.pack(fill='x')
            tk.Label(header, text="📱 Grupo de WhatsApp para Prédicas",
                     font=("Segoe UI", 12, "bold"), bg="#25D366", fg="white").pack()
            tk.Label(header, text="Necesitas configurar esto una sola vez",
                     font=("Segoe UI", 9), bg="#25D366", fg="#d0f5e0").pack()

            frame = tk.Frame(ventana, bg="#f0f0f0", padx=20, pady=15)
            frame.pack(fill='both', expand=True)

            tk.Label(frame,
                     text="Escribe el nombre EXACTO de tu grupo de WhatsApp\n(tal como aparece en la app):",
                     font=("Segoe UI", 10), bg="#f0f0f0", justify='left').pack(anchor='w', pady=(0, 8))

            var_nombre = tk.StringVar()
            entry = tk.Entry(frame, textvariable=var_nombre, font=("Segoe UI", 11), width=35)
            entry.pack(anchor='w', pady=(0, 5))
            entry.focus()

            tk.Label(frame, text="⚠️  Distingue mayúsculas, tildes y espacios",
                     font=("Segoe UI", 8), fg="gray", bg="#f0f0f0").pack(anchor='w')

            frame_btns = tk.Frame(ventana, bg="#f0f0f0", padx=20)
            frame_btns.pack(fill='x', pady=(5, 15))

            def cancelar():
                ventana.destroy()

            def confirmar():
                nombre = var_nombre.get().strip()
                if not nombre:
                    messagebox.showwarning("⚠️ Aviso", "Debes ingresar el nombre del grupo.", parent=ventana)
                    return
                # Guardar en config
                if not cfg.has_section('PREDICACIONES'):
                    cfg.add_section('PREDICACIONES')
                cfg.set('PREDICACIONES', 'nombre_grupo_whatsapp', nombre)
                try:
                    with open(archivo_config, 'w', encoding='utf-8') as f:
                        cfg.write(f)
                except Exception as e:
                    messagebox.showerror("❌ Error", f"No se pudo guardar:\n{e}", parent=ventana)
                    return
                ventana.destroy()
                self._lanzar_extractor()

            tk.Button(frame_btns, text="Cancelar", font=("Segoe UI", 10),
                      bg="#6c757d", fg="white", command=cancelar, width=10).pack(side='left', ipady=4)
            tk.Button(frame_btns, text="✅ Guardar y extraer", font=("Segoe UI", 10, "bold"),
                      bg="#25D366", fg="white", command=confirmar, width=18).pack(side='right', ipady=4)

            self._centrar_ventana(ventana, 420, 260)
            ventana.deiconify()
        else:
            self._lanzar_extractor()

    def _lanzar_extractor(self):
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

    def _abrir_carpeta_mensajes(self):
        """TRIAL: abre la carpeta mensajes en el explorador e informa sobre el gestor"""
        import subprocess as sp
        carpeta = os.path.join(os.path.dirname(self._exe("MensajesBiblicos.exe")), "mensajes")
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        sp.Popen(f'explorer "{carpeta}"')
        messagebox.showinfo(
            "📝 Tus Mensajes",
            "Se abrió tu carpeta de mensajes en el Explorador.\n\n"
            "💡 Con la versión Completa accedes al Gestor de Mensajes:\n"
            "   • Editor visual integrado\n"
            "   • Crear y eliminar mensajes fácilmente\n"
            "   • Contador de caracteres en tiempo real\n\n"
            "Adquiérela en automapro.com"
        )

    def _abrir_gestor_mensajes(self):
        try:
            exe = self._exe("GestorMensajes.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                subprocess.run([sys.executable, "gestor_mensajes_gui.py"])
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo abrir el gestor:\n{e}")

    def _gestionar_tareas(self):
        try:
            exe = self._exe("GestorTareasMensajes.exe")
            if os.path.exists(exe):
                subprocess.run([exe])
            else:
                subprocess.run([sys.executable, "gestor_tareas_gui.py"])
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
            ventana.withdraw()
            ventana.title("📊 Estadísticas")
            ventana.resizable(False, False)
            ventana.configure(bg="#f0f0f0")
            ventana.transient(self.root)
            ventana.grab_set()

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

            self._centrar_ventana(ventana, 400, 370)
            ventana.deiconify()

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


def _verificar_wizard_completado():
    """Si no hay licencia configurada, lanza el wizard y termina"""
    import subprocess
    gestor = GestorLicencias("MensajesBiblicos")
    if not os.path.exists(gestor.archivo_config):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            wizard = os.path.join(base_dir, "WizardMensajes.exe")
        else:
            wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
        
        if os.path.exists(wizard):
            subprocess.Popen([wizard])
        else:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(
                "Configuración requerida",
                "Por favor ejecuta WizardMensajes.exe para configurar el sistema."
            )
            root.destroy()
        return False
    return True


def main():
    if not _verificar_wizard_completado():
        return
    panel = PanelControl()
    panel.ejecutar()


if __name__ == "__main__":
    main()