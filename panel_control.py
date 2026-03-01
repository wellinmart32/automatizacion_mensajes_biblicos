import os
import sys
import tkinter as tk
from tkinter import messagebox
import subprocess
from gestor_licencias import GestorLicencias
from gestor_registro import GestorRegistro
from compartido.toast import Toast


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
            # Sin licencia — lanzar wizard automáticamente
            import subprocess
            if getattr(sys, 'frozen', False):
                wizard = os.path.join(os.path.dirname(sys.executable), "WizardMensajes.exe")
            else:
                wizard = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wizard_primera_vez.py")
            if os.path.exists(wizard):
                subprocess.Popen([wizard])
            else:
                messagebox.showwarning("Sin Licencia", "No hay licencia configurada.\n\nEjecuta el Wizard de primera vez.")
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
                    self._abrir_configurador, row=0, col=1, en_hilo=False)

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

    def _lanzar_subprocess(self, cmd):
        """Para subprocesos externos: bloquea grid, espera cierre del proceso, desbloquea"""
        self._bloquear_grid()
        import threading
        def _hilo():
            try:
                cmd()
            finally:
                pass  # El cmd maneja su propio desbloqueo
        threading.Thread(target=_hilo, daemon=True).start()

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

        # Acción 5 — Ejecutar Secuencia Configurada
        if es_full:
            tk.Button(
                frame,
                text="⚡  Ejecutar Secuencia Configurada",
                font=("Segoe UI", 11, "bold"),
                bg="#e65100",
                fg="white",
                activebackground="#bf360c",
                cursor="hand2",
                anchor='w',
                padx=15,
                pady=8,
                command=lambda: [ventana.destroy(), self._ejecutar_secuencia()]
            ).pack(fill='x', pady=(0, 8))
        else:
            tk.Button(
                frame,
                text="🔒  Ejecutar Secuencia Configurada  —  versión Completa",
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
            width=12,
            command=ventana.destroy
        ).pack(pady=15)

        self._centrar_ventana(ventana, 500, 470)
        ventana.deiconify()

    # ==================== ACCIONES ====================

    def _ejecutar_secuencia(self):
        """Ejecuta los módulos en el orden configurado en Secuencia"""
        import configparser
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(self.base_dir, "config_global.txt"), encoding='utf-8')
        modulos = cfg.get('SECUENCIA', 'modulos_activos', fallback='').strip()

        if not modulos:
            respuesta = messagebox.askokcancel(
                "⚙️ Secuencia no configurada",
                "No has configurado la secuencia de módulos.\n\n"
                "¿Deseas ir al Configurador para definirla ahora?"
            )
            if respuesta:
                self._abrir_configurador(pestaña='secuencia')
            return

        lista = [m.strip() for m in modulos.split(',') if m.strip()]

        # Validar configuración antes de ejecutar
        necesita_grupo = 'extraer' in lista or 'publicar_predica' in lista
        if necesita_grupo:
            grupo = cfg.get('PREDICACIONES', 'nombre_grupo_whatsapp', fallback='').strip()
            if not grupo:
                respuesta = messagebox.askokcancel(
                    "⚠️ Configuración incompleta",
                    "La secuencia incluye 'Extraer Predicaciones' pero no has configurado\n"
                    "el nombre del grupo de WhatsApp.\n\n"
                    "¿Deseas ir al Configurador para completarlo ahora?"
                )
                if respuesta:
                    self._abrir_configurador(pestana='extractor')
                return

        from compartido.gestor_archivos import leer_estado_predicaciones

        for modulo in lista:
            try:
                if modulo == 'biblico':
                    self._publicar_facebook()

                elif modulo == 'extraer':
                    self._extraer_predicaciones()

                elif modulo == 'publicar_predica':
                    # Verificar si hay predicaciones pendientes
                    estado = leer_estado_predicaciones()
                    hay_pendientes = estado.get('pendientes', 0) > 0
                    if hay_pendientes:
                        self._publicar_predicaciones()
                    else:
                        # No hay pendientes — extraer primero si no está ya en la secuencia
                        if 'extraer' not in lista:
                            respuesta = messagebox.askokcancel(
                                "📭 Sin predicaciones",
                                "No hay predicaciones extraídas.\n\n"
                                "¿Deseas extraer predicaciones ahora antes de publicar?"
                            )
                            if respuesta:
                                self._extraer_predicaciones()
                        # Si extraer ya está en la secuencia, fue ejecutado antes — skip publicar

                elif modulo == 'oraciones':
                    self._enviar_oraciones()

            except Exception as e:
                messagebox.showerror("❌ Error en secuencia", f"Error ejecutando '{modulo}':\n{e}")
                break

    def _publicar_facebook(self):
        try:
            exe = self._exe("MensajesBiblicos.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe, "--solo-biblico"])
            else:
                subprocess.Popen([sys.executable, "flujo_completo_facebook.py", "--solo-biblico"])
            self._toast("✅ Publicación iniciada", "El navegador se abrirá en unos segundos...")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar la publicación:\n{e}")

    def _enviar_oraciones(self):
        """Ejecuta envío de oraciones usando destinatarios configurados por defecto"""
        import json

        archivo_grupos = os.path.join(self.base_dir, "llamados-oracion", "grupos.json")

        if not os.path.exists(archivo_grupos):
            respuesta = messagebox.askokcancel(
                "⚠️ Sin grupos configurados",
                "No hay grupos de oración configurados.\n\n"
                "¿Deseas abrir el Configurador para agregarlos ahora?"
            )
            if respuesta:
                self._abrir_configurador(pestaña='oraciones')
            return

        try:
            with open(archivo_grupos, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            grupos = [g for g in datos.get('grupos', []) if g.get('seleccionado', True) and g.get('activo', True)]
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error leyendo grupos:\n{e}")
            return

        if not grupos:
            respuesta = messagebox.askokcancel(
                "⚠️ Sin destinatarios seleccionados",
                "No hay destinatarios seleccionados por defecto.\n\n"
                "¿Deseas abrir el Configurador para configurarlos ahora?"
            )
            if respuesta:
                self._abrir_configurador(pestaña='oraciones')
            return

        try:
            exe = self._exe("OracionesWhatsApp.exe")
            if os.path.exists(exe):
                subprocess.Popen([exe])
            else:
                subprocess.Popen([sys.executable, os.path.join("publicadores", "whatsapp_oracion.py")])
            self._toast("📱 Oraciones WhatsApp", f"Enviando a {len(grupos)} destinatario(s)...")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo iniciar el módulo:\n{e}")

    def _abrir_configurador(self, pestaña=None, pestana=None):
        """Abre el configurador — bloquea el grid mientras está abierto"""
        if getattr(self, '_configurador_abierto', False):
            return
        self._configurador_abierto = True
        try:
            exe = self._exe("ConfiguradorMensajes.exe")
            pestana_final = pestaña or pestana
            args = [exe] if os.path.exists(exe) else [sys.executable, "configurador_gui.py"]
            if pestana_final:
                args.append(f"--pestana={pestana_final}")

            proceso = subprocess.Popen(args)
            self.root.after(350, self._bloquear_grid)

            def _esperar_cierre():
                proceso.wait()
                self._configurador_abierto = False
                self.root.after(0, self._desbloquear_grid)

            import threading
            threading.Thread(target=_esperar_cierre, daemon=True).start()

        except Exception as e:
            self._configurador_abierto = False
            self._desbloquear_grid()
            messagebox.showerror("❌ Error", f"No se pudo abrir el configurador:\n{e}")

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
        self._toast(
            "📝 Tus Mensajes",
            "Carpeta abierta — version Completa incluye editor visual",
            duracion=5000
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
            stats = gestor.obtener_estadisticas()
            fecha_ultima = stats.get('ultima_publicacion') or 'Nunca'

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
        """Delega al sistema centralizado de toasts"""
        from compartido.toast import Toast
        if color == Toast.COLOR_ERROR or color == "#dc3545":
            Toast.error(self.root, f"{titulo}\n{mensaje}", duracion)
        elif color == Toast.COLOR_ADVERTENCIA or color == "#e65100":
            Toast.advertencia(self.root, f"{titulo}\n{mensaje}", duracion)
        elif color == Toast.COLOR_INFO or color == "#1a73e8":
            Toast.info(self.root, f"{titulo}\n{mensaje}", duracion)
        else:
            Toast.exito(self.root, f"{titulo}\n{mensaje}", duracion)

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