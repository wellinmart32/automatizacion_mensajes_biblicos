import os
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from gestor_licencias import GestorLicencias


class WizardPrimeraVez:
    """Wizard de configuración inicial para primera ejecución"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎉 Bienvenido - Mensajes Bíblicos")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # Centrar ventana
        self.root.withdraw()
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.deiconify()

        self.paso_actual = 0
        self.datos_config = {
            'codigo_licencia': '',
            'navegador': 'firefox',
            'usar_perfil': 'si',
            'usar_ejemplos': False
        }
        self.gestor_licencias = GestorLicencias()

        self._mostrar_paso()

    def _limpiar_ventana(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def _mostrar_paso(self):
        """Muestra el paso actual del wizard"""
        self._limpiar_ventana()

        if self.paso_actual == 0:
            self._paso_bienvenida()
        elif self.paso_actual == 1:
            self._paso_licencia()
        elif self.paso_actual == 2:
            self._paso_configuracion()
        elif self.paso_actual == 3:
            self._paso_mensajes()
        elif self.paso_actual == 4:
            self._paso_finalizar()

    def _paso_bienvenida(self):
        """Paso 0: Pantalla de bienvenida"""
        # Header
        header = tk.Frame(self.root, bg="#1a73e8", pady=20)
        header.pack(fill='x')
        tk.Label(
            header,
            text="🎉 Bienvenido a Mensajes Bíblicos",
            font=("Segoe UI", 16, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Esta aplicación publica mensajes bíblicos\nen Facebook de forma automática.",
            font=("Segoe UI", 12),
            bg="#f0f0f0",
            justify='center'
        ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Vamos a configurarla juntos paso a paso\n(solo esta vez).",
            font=("Segoe UI", 11),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 30))

        tk.Label(
            frame,
            text="✨ Características:\n\n"
                 "• Publicación automática en Facebook\n"
                 "• Rotación inteligente de mensajes\n"
                 "• Integración con predicaciones de WhatsApp\n"
                 "• Programación de tareas (versión FULL)",
            font=("Segoe UI", 10),
            bg="#f0f0f0",
            justify='left'
        ).pack(pady=(0, 30))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="▶️  Comenzar",
            font=("Segoe UI", 11, "bold"),
            bg="#1a73e8",
            fg="white",
            width=20,
            command=self._siguiente
        ).pack()

    def _paso_licencia(self):
        """Paso 1: Activar licencia"""
        # Header
        header = tk.Frame(self.root, bg="#1a73e8", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 1 de 4: Activar Licencia",
            font=("Segoe UI", 14, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Ingresa tu código de licencia:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 10))

        self.entry_licencia = tk.Entry(
            frame,
            font=("Segoe UI", 12),
            width=35
        )
        self.entry_licencia.pack(pady=(0, 20))
        self.entry_licencia.focus()
        
        # Auto-mayúsculas mientras escribe
        def auto_mayusculas(event):
            contenido = self.entry_licencia.get()
            mayus = contenido.upper()
            if contenido != mayus:
                pos = self.entry_licencia.index(tk.INSERT)
                self.entry_licencia.delete(0, tk.END)
                self.entry_licencia.insert(0, mayus)
                self.entry_licencia.icursor(pos)
        
        self.entry_licencia.bind('<KeyRelease>', auto_mayusculas)

        tk.Label(
            frame,
            text="Si no tienes código, puedes usar la versión TRIAL\n"
                 "(limitada a 5 mensajes por día)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray",
            justify='center'
        ).pack(pady=(0, 30))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="Usar TRIAL",
            font=("Segoe UI", 10),
            bg="#ffc107",
            width=12,
            command=self._usar_trial
        ).pack(side='left', padx=10)

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#1a73e8",
            fg="white",
            width=12,
            command=self._validar_licencia
        ).pack(side='right', padx=(10, 40))

    def _paso_configuracion(self):
        """Paso 2: Configuración básica"""
        # Header
        header = tk.Frame(self.root, bg="#1a73e8", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 2 de 4: Configuración",
            font=("Segoe UI", 14, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="Navegador:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        self.var_navegador = tk.StringVar(value="firefox")
        frame_nav = tk.Frame(frame, bg="#f0f0f0")
        frame_nav.pack(anchor='w', pady=(0, 20))
        
        tk.Radiobutton(
            frame_nav, text="Firefox",
            variable=self.var_navegador, value="firefox",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(
            frame_nav, text="Chrome",
            variable=self.var_navegador, value="chrome",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left')

        tk.Label(
            frame,
            text="Usar tu sesión de Facebook guardada:",
            font=("Segoe UI", 11, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(20, 5))

        tk.Label(
            frame,
            text="(Recomendado: Sí - para no tener que iniciar sesión cada vez)",
            font=("Segoe UI", 9),
            bg="#f0f0f0",
            fg="gray"
        ).pack(anchor='w', pady=(0, 5))

        self.var_perfil = tk.StringVar(value="si")
        frame_perfil = tk.Frame(frame, bg="#f0f0f0")
        frame_perfil.pack(anchor='w', pady=(0, 20))
        
        tk.Radiobutton(
            frame_perfil, text="Sí",
            variable=self.var_perfil, value="si",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left', padx=(0, 20))
        
        tk.Radiobutton(
            frame_perfil, text="No",
            variable=self.var_perfil, value="no",
            bg="#f0f0f0", font=("Segoe UI", 10)
        ).pack(side='left')

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#1a73e8",
            fg="white",
            width=12,
            command=self._guardar_config_basica
        ).pack(side='right', padx=(10, 40))

    def _paso_mensajes(self):
        """Paso 3: Crear mensajes o usar ejemplos"""
        # Header
        header = tk.Frame(self.root, bg="#1a73e8", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 3 de 4: Tus Mensajes",
            font=("Segoe UI", 14, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        # Verificar si ya hay mensajes
        mensajes_existentes = len([f for f in os.listdir('mensajes') if f.endswith('.txt')]) if os.path.exists('mensajes') else 0

        if mensajes_existentes > 0:
            tk.Label(
                frame,
                text=f"✅ Ya tienes {mensajes_existentes} mensajes creados",
                font=("Segoe UI", 12, "bold"),
                bg="#f0f0f0",
                fg="#28a745"
            ).pack(pady=(0, 20))
        else:
            tk.Label(
                frame,
                text="La aplicación necesita mensajes para publicar.",
                font=("Segoe UI", 11),
                bg="#f0f0f0"
            ).pack(pady=(0, 20))

        tk.Label(
            frame,
            text="Opciones:",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 10))

        # Opción 1
        frame_op1 = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
        frame_op1.pack(fill='x', pady=(0, 15), padx=20)
        
        tk.Label(
            frame_op1,
            text="📝 Crear mis propios mensajes ahora",
            font=("Segoe UI", 10, "bold"),
            bg="white"
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        tk.Label(
            frame_op1,
            text="Abre el gestor y crea mensajes personalizados",
            font=("Segoe UI", 9),
            bg="white",
            fg="gray"
        ).pack(anchor='w', padx=15, pady=(0, 10))
        
        tk.Button(
            frame_op1,
            text="Abrir Gestor de Mensajes",
            font=("Segoe UI", 9),
            bg="#1a73e8",
            fg="white",
            command=self._abrir_gestor_mensajes
        ).pack(anchor='w', padx=15, pady=(0, 10))

        if mensajes_existentes == 0:
            # Opción 2 - solo si no hay mensajes
            frame_op2 = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
            frame_op2.pack(fill='x', pady=(0, 15), padx=20)
            
            tk.Label(
                frame_op2,
                text="📋 Usar mensajes de ejemplo",
                font=("Segoe UI", 10, "bold"),
                bg="white"
            ).pack(anchor='w', padx=15, pady=(10, 5))
            
            tk.Label(
                frame_op2,
                text="Instala 5 mensajes bíblicos de ejemplo para comenzar",
                font=("Segoe UI", 9),
                bg="white",
                fg="gray"
            ).pack(anchor='w', padx=15, pady=(0, 10))
            
            tk.Button(
                frame_op2,
                text="Usar Ejemplos",
                font=("Segoe UI", 9),
                bg="#28a745",
                fg="white",
                command=self._usar_ejemplos
            ).pack(anchor='w', padx=15, pady=(0, 10))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="◀️ Atrás",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=12,
            command=self._anterior
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="Siguiente ▶️",
            font=("Segoe UI", 10, "bold"),
            bg="#1a73e8",
            fg="white",
            width=12,
            command=self._verificar_mensajes
        ).pack(side='right', padx=(10, 40))

    def _paso_finalizar(self):
        """Paso 4: Finalizar configuración"""
        # Header
        header = tk.Frame(self.root, bg="#28a745", pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text="Paso 4 de 4: ¡Listo!",
            font=("Segoe UI", 14, "bold"),
            bg="#28a745",
            fg="white"
        ).pack()

        # Contenido
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(fill='both', expand=True, padx=40, pady=30)

        tk.Label(
            frame,
            text="✅ ¡Configuración completada!",
            font=("Segoe UI", 14, "bold"),
            bg="#f0f0f0",
            fg="#28a745"
        ).pack(pady=(0, 20))

        # Resumen
        resumen_frame = tk.Frame(frame, bg="white", relief='solid', borderwidth=1)
        resumen_frame.pack(fill='x', pady=(0, 20))

        licencia_texto = "TRIAL" if not self.datos_config['codigo_licencia'] else self.datos_config['codigo_licencia'][:20] + "..."
        mensajes_count = len([f for f in os.listdir('mensajes') if f.endswith('.txt')]) if os.path.exists('mensajes') else 0

        items = [
            ("✅ Licencia:", licencia_texto),
            ("✅ Navegador:", self.datos_config['navegador'].capitalize()),
            ("✅ Mensajes listos:", f"{mensajes_count} mensajes")
        ]

        for label, valor in items:
            item_frame = tk.Frame(resumen_frame, bg="white")
            item_frame.pack(fill='x', padx=15, pady=5)
            tk.Label(item_frame, text=label, font=("Segoe UI", 10, "bold"), bg="white", width=20, anchor='w').pack(side='left')
            tk.Label(item_frame, text=valor, font=("Segoe UI", 10), bg="white", anchor='w').pack(side='left')

        tk.Label(
            frame,
            text="¿Quieres hacer la primera publicación ahora mismo?",
            font=("Segoe UI", 11),
            bg="#f0f0f0"
        ).pack(pady=(20, 10))

        # Botones
        frame_btn = tk.Frame(self.root, bg="#f0f0f0", pady=20)
        frame_btn.pack(fill='x', side='bottom')

        tk.Button(
            frame_btn,
            text="❌ Ahora no",
            font=("Segoe UI", 10),
            bg="#e0e0e0",
            width=15,
            command=self._finalizar_sin_publicar
        ).pack(side='left', padx=(40, 10))

        tk.Button(
            frame_btn,
            text="▶️ Publicar Ahora",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            command=self._publicar_ahora
        ).pack(side='right', padx=(10, 40))

    # Funciones auxiliares
    def _siguiente(self):
        self.paso_actual += 1
        self._mostrar_paso()

    def _anterior(self):
        self.paso_actual -= 1
        self._mostrar_paso()

    def _usar_trial(self):
        self.datos_config['codigo_licencia'] = ''
        self._siguiente()

    def _validar_licencia(self):
        codigo = self.entry_licencia.get().strip().upper()
        
        # Formatear: quitar guiones, convertir mayúsculas, agregar guiones
        if codigo:
            # Quitar guiones existentes
            codigo_limpio = codigo.replace('-', '')
            
            # Si tiene el formato correcto de cantidad de caracteres, formatear
            # Formato esperado: LIC-MASTER-WELLI (3-6-5 caracteres)
            if len(codigo_limpio) >= 10:
                codigo = f"{codigo_limpio[:3]}-{codigo_limpio[3:9]}-{codigo_limpio[9:]}"
            
            self.datos_config['codigo_licencia'] = codigo
            self.gestor_licencias.guardar_codigo_licencia(codigo)
        
        self._siguiente()

    def _guardar_config_basica(self):
        self.datos_config['navegador'] = self.var_navegador.get()
        self.datos_config['usar_perfil'] = self.var_perfil.get()
        self._siguiente()

    def _abrir_gestor_mensajes(self):
        try:
            import subprocess
            subprocess.Popen(['python', 'gestor_mensajes_gui.py'])
            messagebox.showinfo("Info", "El gestor de mensajes se abrió en una nueva ventana.\n\nCrea al menos 1 mensaje y luego presiona 'Siguiente'.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el gestor: {e}")

    def _usar_ejemplos(self):
        try:
            os.makedirs('mensajes', exist_ok=True)
            
            # Verificar si ya existen archivos
            archivos_existentes = [f for f in os.listdir('mensajes') if f.startswith('ejemplo-') and f.endswith('.txt')]
            numero_inicio = len(archivos_existentes) + 1
            
            ejemplos = [
                "Confía en el Señor con todo tu corazón y no te apoyes en tu propia prudencia. - Proverbios 3:5",
                "Todo lo puedo en Cristo que me fortalece. - Filipenses 4:13",
                "El Señor es mi pastor, nada me faltará. - Salmos 23:1",
                "Mas buscad primeramente el reino de Dios y su justicia. - Mateo 6:33",
                "Porque de tal manera amó Dios al mundo, que ha dado a su Hijo unigénito. - Juan 3:16"
            ]
            
            archivos_creados = []
            for i, texto in enumerate(ejemplos, numero_inicio):
                nombre_archivo = f'ejemplo-{i:03d}.txt'
                with open(f'mensajes/{nombre_archivo}', 'w', encoding='utf-8') as f:
                    f.write(texto)
                archivos_creados.append(nombre_archivo)
            
            self.datos_config['usar_ejemplos'] = True
            messagebox.showinfo("✅ Éxito", f"Se instalaron {len(ejemplos)} mensajes de ejemplo:\n\n" + "\n".join(archivos_creados))
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron crear los ejemplos: {e}")

    def _verificar_mensajes(self):
        mensajes = len([f for f in os.listdir('mensajes') if f.endswith('.txt')]) if os.path.exists('mensajes') else 0
        if mensajes == 0:
            messagebox.showwarning("Aviso", "Necesitas al menos un mensaje para continuar.\n\nCrea mensajes o usa los ejemplos.")
            return
        self._crear_config_completa()
        self._siguiente()

    def _crear_config_completa(self):
        """Crea el archivo config_global.txt con la configuración inicial completa"""
        config = configparser.ConfigParser()
        
        config['GENERAL'] = {
            'nombre_proyecto': 'Publicador Automático Facebook',
            'carpeta_mensajes': 'mensajes',
            'navegador': self.datos_config['navegador'],
            'modo_debug': 'si'
        }
        
        config['MENSAJES'] = {
            'seleccion': 'aleatoria',
            'historial_evitar_repetir': '5',
            'formato_fecha': 'no',
            'agregar_hashtags': 'no',
            'hashtags': '#Fe,#Biblia,#Reflexión',
            'agregar_firma': 'no',
            'texto_firma': 'Publicado automáticamente'
        }
        
        config['PUBLICACION'] = {
            'tiempo_entre_intentos': '3',
            'max_intentos_por_publicacion': '3',
            'espera_despues_publicar': '5',
            'verificar_publicacion_exitosa': 'si',
            'espera_estabilizacion_modal': '3'
        }
        
        config['NAVEGADOR'] = {
            'usar_perfil_existente': self.datos_config['usar_perfil'],
            'carpeta_perfil_custom': 'perfiles/facebook_publicador',
            'desactivar_notificaciones': 'si',
            'maximizar_ventana': 'si'
        }
        
        config['LIMITES'] = {
            'tiempo_minimo_entre_publicaciones_segundos': '120',
            'permitir_duplicados': 'no',
            'permitir_forzar_publicacion_manual': 'si'
        }
        
        config['PREDICACIONES'] = {
            'activar_predicaciones': 'no',
            'alternar_con_predicaciones': 'no',
            'nombre_grupo_whatsapp': 'Prédicas',
            'mensajes_por_extraccion': '10',
            'agregar_introduccion_predica': 'si',
            'texto_introduccion_predica': '⏰ Vale la pena ver esto',
            'agregar_hashtags_predicaciones': 'no',
            'hashtags_predicaciones': '',
            'tiempo_espera_previsualizacion': '12',
            'usar_estrategia_optimizada_enlaces': 'si'
        }
        
        config['DEBUG'] = {
            'modo_debug': 'detallado'
        }
        
        with open('config_global.txt', 'w', encoding='utf-8') as f:
            f.write("# ============================================================\n")
            f.write("# CONFIGURACIÓN GLOBAL - PUBLICADOR AUTOMÁTICO FACEBOOK\n")
            f.write("# ============================================================\n\n")
            config.write(f)

    def _finalizar_sin_publicar(self):
        messagebox.showinfo(
            "✅ Configuración Completada",
            "¡Todo listo!\n\nPuedes ejecutar 'Mensajes Bíblicos' cuando quieras publicar.\n\nO usa 'Panel de Control' para gestionar tu aplicación."
        )
        self.root.destroy()

    def _publicar_ahora(self):
        try:
            import subprocess
            subprocess.Popen(['python', 'publicar_facebook.py'])
            messagebox.showinfo(
                "▶️ Publicando",
                "Se abrirá el navegador y comenzará la publicación.\n\nEsto puede tomar unos segundos..."
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo iniciar la publicación: {e}")

    def ejecutar(self):
        self.root.mainloop()


def main():
    wizard = WizardPrimeraVez()
    wizard.ejecutar()


if __name__ == "__main__":
    main()