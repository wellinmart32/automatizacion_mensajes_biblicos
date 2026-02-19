import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from datetime import datetime
from gestor_licencias import GestorLicencias


class GestorTareasGUI:
    """Gestor de tareas automáticas - Windows Task Scheduler"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🗓️ Gestor de Tareas Automáticas")
        self.root.geometry("800x600")
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
        if not self._verificar_licencia_full():
            messagebox.showerror(
                "Licencia Requerida",
                "Esta función requiere licencia FULL.\n\nActualiza tu licencia para acceder."
            )
            self.root.destroy()
            return

        self.prefijo_tarea = "AutomaPro_MensajesBiblicos"
        self.ruta_script = os.path.abspath("publicar_facebook.py")
        
        self.dias_map = {
            'L': 'MON', 'M': 'TUE', 'X': 'WED', 
            'J': 'THU', 'V': 'FRI', 'S': 'SAT', 'D': 'SUN'
        }
        
        self.dias_map_inverso = {
            'MON': 'L', 'TUE': 'M', 'WED': 'X',
            'THU': 'J', 'FRI': 'V', 'SAT': 'S', 'SUN': 'D'
        }

        self._construir_ui()
        self._cargar_tareas()

    def _mostrar_toast(self, mensaje, duracion=3000, color="#28a745"):
        """Muestra notificación toast que desaparece automáticamente"""
        toast = tk.Toplevel(self.root)
        toast.withdraw()
        toast.overrideredirect(True)
        
        frame = tk.Frame(toast, bg=color, padx=20, pady=15)
        frame.pack()
        
        tk.Label(
            frame,
            text=mensaje,
            font=("Segoe UI", 11),
            bg=color,
            fg="white"
        ).pack()
        
        toast.update_idletasks()
        width = toast.winfo_width()
        height = toast.winfo_height()
        x = (toast.winfo_screenwidth() // 2) - (width // 2)
        y = toast.winfo_screenheight() - height - 50
        
        toast.geometry(f'+{x}+{y}')
        toast.deiconify()
        
        toast.after(duracion, toast.destroy)

    def _verificar_licencia_full(self):
        """Verifica que la licencia sea FULL o MASTER"""
        codigo = self.gestor_licencias.obtener_codigo_guardado()
        
        if not codigo:
            return False
        
        resultado = self.gestor_licencias.verificar_licencia(codigo, mostrar_mensajes=False)
        
        if not resultado['valida']:
            return False
        
        if resultado.get('developer_permanente') or resultado.get('tipo') == 'FULL':
            return True
        
        return False

    def _construir_ui(self):
        """Construye la interfaz gráfica"""
        header = tk.Frame(self.root, bg="#1a73e8", pady=20)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="🗓️ Gestor de Tareas Automáticas",
            font=("Segoe UI", 16, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()
        
        tk.Label(
            header,
            text="Programa publicaciones automáticas en días y horarios específicos",
            font=("Segoe UI", 10),
            bg="#1a73e8",
            fg="white"
        ).pack()

        toolbar = tk.Frame(self.root, bg="#f0f0f0", pady=15)
        toolbar.pack(fill='x', padx=20)
        
        tk.Button(
            toolbar,
            text="➕ Nueva Tarea",
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=15,
            command=self._nueva_tarea
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            toolbar,
            text="✏️ Editar",
            font=("Segoe UI", 10),
            bg="#ffc107",
            width=12,
            command=self._editar_tarea
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            toolbar,
            text="🔄 Actualizar",
            font=("Segoe UI", 10),
            bg="#17a2b8",
            fg="white",
            width=12,
            command=self._cargar_tareas
        ).pack(side='left', padx=(0, 10))
        
        tk.Button(
            toolbar,
            text="🗑️ Eliminar",
            font=("Segoe UI", 10),
            bg="#dc3545",
            fg="white",
            width=12,
            command=self._eliminar_tarea
        ).pack(side='left')

        frame_lista = tk.Frame(self.root, bg="#f0f0f0")
        frame_lista.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')
        
        self.tree = ttk.Treeview(
            frame_lista,
            columns=('nombre', 'dias', 'proxima', 'estado'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        
        self.tree.heading('nombre', text='Nombre de Tarea')
        self.tree.heading('dias', text='Días')
        self.tree.heading('proxima', text='Próxima Ejecución')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('nombre', width=300)
        self.tree.column('dias', width=100)
        self.tree.column('proxima', width=200)
        self.tree.column('estado', width=100)
        
        self.tree.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree.yview)
        
        self.tree.bind('<Double-1>', lambda e: self._editar_tarea())

    def _cargar_tareas(self):
        """Carga las tareas programadas del sistema"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            resultado = subprocess.run(
                ['schtasks', '/Query', '/FO', 'LIST'],
                capture_output=True,
                text=True,
                encoding='cp850',
                errors='ignore'
            )
            
            if resultado.returncode != 0:
                self.tree.insert('', 'end', values=('Error cargando tareas', '', '', ''))
                return
            
            tareas_encontradas = []
            lineas = resultado.stdout.split('\n')
            
            tarea_actual = None
            for linea in lineas:
                linea = linea.strip()
                
                if linea.startswith('Nombre de tarea:'):
                    nombre_tarea = linea.split(':', 1)[1].strip()
                    
                    if self.prefijo_tarea in nombre_tarea:
                        tarea_actual = nombre_tarea
                
                elif tarea_actual and linea.startswith('Estado:'):
                    estado = linea.split(':', 1)[1].strip()
                    
                    detalles = self._obtener_detalles_tarea(tarea_actual)
                    
                    proxima_ejecucion = detalles.get('Hora próxima ejecución', 'N/A')
                    dias_texto = self._extraer_dias_cortos(detalles)
                    
                    tareas_encontradas.append((tarea_actual, dias_texto, proxima_ejecucion, estado))
                    tarea_actual = None
            
            if not tareas_encontradas:
                self.tree.insert('', 'end', values=('No hay tareas programadas', '', '', ''))
            else:
                for tarea in tareas_encontradas:
                    self.tree.insert('', 'end', values=tarea)
        
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar tareas:\n{e}")

    def _obtener_detalles_tarea(self, nombre_tarea):
        """Obtiene detalles de una tarea específica"""
        try:
            resultado = subprocess.run(
                ['schtasks', '/Query', '/TN', nombre_tarea, '/FO', 'LIST', '/V'],
                capture_output=True,
                text=True,
                encoding='cp850',
                errors='ignore'
            )
            
            if resultado.returncode != 0:
                return {}
            
            detalles = {}
            for linea in resultado.stdout.split('\n'):
                if ':' in linea:
                    clave, valor = linea.split(':', 1)
                    detalles[clave.strip()] = valor.strip()
            
            return detalles
        
        except Exception as e:
            print(f"Error obteniendo detalles: {e}")
            return {}

    def _extraer_dias_cortos(self, detalles):
        """Extrae días en formato corto (LMXJV)"""
        tipo_prog = detalles.get('Tipo de programación', '').lower()
        dias = detalles.get('Días', '')
        
        if 'diaria' in tipo_prog or 'daily' in tipo_prog:
            return 'Diario'
        
        if not dias or dias == 'N/A':
            return 'Semanal'
        
        dias_map_eng = {
            'mon': 'L', 'tue': 'M', 'wed': 'X', 'thu': 'J',
            'fri': 'V', 'sat': 'S', 'sun': 'D'
        }
        
        dias_lower = dias.lower()
        dias_cortos = []
        
        for eng, esp in dias_map_eng.items():
            if eng in dias_lower:
                dias_cortos.append(esp)
        
        return ''.join(dias_cortos) if dias_cortos else 'Semanal'

    def _editar_tarea(self):
        """Abre diálogo para editar tarea seleccionada"""
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para editar")
            return
        
        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]
        
        if nombre_tarea == 'No hay tareas programadas':
            return
        
        if nombre_tarea.startswith('\\'):
            nombre_tarea = nombre_tarea[1:]
        
        detalles = self._obtener_detalles_tarea(nombre_tarea)
        
        if not detalles:
            messagebox.showerror("Error", "No se pudieron obtener los detalles de la tarea")
            return
        
        horario_actual = detalles.get('Hora de inicio', '09:00:00')
        try:
            hora_parts = horario_actual.split(':')
            hora_inicial = hora_parts[0]
            minuto_inicial = hora_parts[1]
        except:
            hora_inicial = '09'
            minuto_inicial = '00'
        
        tipo_programacion = detalles.get('Tipo de programación', '').lower()
        dias_actuales = detalles.get('Días', '')
        
        es_diaria = 'diaria' in tipo_programacion or 'daily' in tipo_programacion

        self._mostrar_formulario_tarea(
            titulo=f"✏️ Editar: {nombre_tarea}",
            color_header="#ffc107",
            nombre_tarea=nombre_tarea,
            hora_inicial=hora_inicial,
            minuto_inicial=minuto_inicial,
            es_diaria=es_diaria,
            dias_iniciales=dias_actuales,
            es_edicion=True
        )

    def _nueva_tarea(self):
        """Abre diálogo para crear nueva tarea"""
        nombre_auto = f"{self.prefijo_tarea}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
        self._mostrar_formulario_tarea(
            titulo="➕ Nueva Tarea Automática",
            color_header="#28a745",
            nombre_tarea=nombre_auto,
            hora_inicial="09",
            minuto_inicial="00",
            es_diaria=True,
            dias_iniciales="",
            es_edicion=False
        )

    def _mostrar_formulario_tarea(self, titulo, color_header, nombre_tarea, hora_inicial, minuto_inicial, es_diaria, dias_iniciales, es_edicion):
        """Muestra formulario unificado para crear/editar tareas"""
        ventana = tk.Toplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("600x600")
        ventana.configure(bg="#f0f0f0")
        ventana.transient(self.root)
        ventana.grab_set()
        
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (300)
        y = (ventana.winfo_screenheight() // 2) - (300)
        ventana.geometry(f'600x600+{x}+{y}')
        
        header = tk.Frame(ventana, bg=color_header, pady=15)
        header.pack(fill='x')
        tk.Label(
            header,
            text=titulo,
            font=("Segoe UI", 14, "bold"),
            bg=color_header,
            fg="white" if color_header != "#ffc107" else "black"
        ).pack()
        
        form = tk.Frame(ventana, bg="#f0f0f0")
        form.pack(fill='both', expand=True, padx=30, pady=15)
        
        tk.Label(form, text="Nombre de la tarea:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 3))
        
        if es_edicion:
            tk.Label(form, text=nombre_tarea, font=("Segoe UI", 10), bg="#f0f0f0", fg="gray").pack(anchor='w', pady=(0, 10))
            entry_nombre = None
        else:
            entry_nombre = tk.Entry(form, font=("Segoe UI", 10), width=50)
            entry_nombre.pack(anchor='w', pady=(0, 10))
            entry_nombre.insert(0, nombre_tarea)
        
        tk.Label(form, text="Frecuencia:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 3))
        var_frecuencia = tk.StringVar(value="DAILY" if es_diaria else "WEEKLY")
        
        frame_freq = tk.Frame(form, bg="#f0f0f0")
        frame_freq.pack(anchor='w', pady=(0, 10))
        
        def cambio_frecuencia():
            if var_frecuencia.get() == "DAILY":
                frame_dias.pack_forget()
            else:
                frame_dias.pack(after=frame_freq, anchor='w', pady=(0, 10))
        
        tk.Radiobutton(frame_freq, text="Diaria", variable=var_frecuencia, value="DAILY", bg="#f0f0f0", command=cambio_frecuencia).pack(side='left', padx=(0, 15))
        tk.Radiobutton(frame_freq, text="Semanal", variable=var_frecuencia, value="WEEKLY", bg="#f0f0f0", command=cambio_frecuencia).pack(side='left')
        
        tk.Label(form, text="Días de la semana:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(0, 3))
        
        frame_dias = tk.Frame(form, bg="#f0f0f0")
        if not es_diaria:
            frame_dias.pack(anchor='w', pady=(0, 10))
        
        dias_vars = {}
        dias_labels = [('L', 'Lunes'), ('M', 'Martes'), ('X', 'Miércoles'), ('J', 'Jueves'), 
                      ('V', 'Viernes'), ('S', 'Sábado'), ('D', 'Domingo')]
        
        dias_seleccionados = []
        if dias_iniciales:
            dias_lower = dias_iniciales.lower()
            for eng_day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
                if eng_day in dias_lower:
                    dias_seleccionados.append(self.dias_map_inverso[eng_day.upper()])
        
        for corto, completo in dias_labels:
            var = tk.BooleanVar(value=corto in dias_seleccionados)
            dias_vars[corto] = var
            tk.Checkbutton(frame_dias, text=completo, variable=var, bg="#f0f0f0").pack(anchor='w', pady=1)
        
        tk.Label(form, text="Horario (HH:MM formato 24h):", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").pack(anchor='w', pady=(5, 3))
        
        frame_hora = tk.Frame(form, bg="#f0f0f0")
        frame_hora.pack(anchor='w', pady=(0, 5))
        
        vcmd_hora = (ventana.register(lambda text: len(text) <= 2 and (text.isdigit() or text == "")), '%P')
        
        entry_hora = tk.Entry(frame_hora, font=("Segoe UI", 10), width=5, validate='key', validatecommand=vcmd_hora)
        entry_hora.pack(side='left')
        entry_hora.insert(0, hora_inicial)
        
        tk.Label(frame_hora, text=":", font=("Segoe UI", 10), bg="#f0f0f0").pack(side='left', padx=5)
        
        entry_minuto = tk.Entry(frame_hora, font=("Segoe UI", 10), width=5, validate='key', validatecommand=vcmd_hora)
        entry_minuto.pack(side='left')
        entry_minuto.insert(0, minuto_inicial)
        
        def auto_salto_hora(event):
            contenido = entry_hora.get()
            if len(contenido) == 2:
                entry_minuto.focus()
                entry_minuto.select_range(0, tk.END)
        
        entry_hora.bind('<KeyRelease>', auto_salto_hora)
        
        frame_btns = tk.Frame(ventana, bg="#f0f0f0")
        frame_btns.pack(fill='x', side='bottom', pady=(5, 15))
        
        tk.Button(
            frame_btns,
            text="Cancelar",
            font=("Segoe UI", 10),
            bg="#6c757d",
            fg="white",
            width=12,
            command=ventana.destroy
        ).pack(side='left', padx=(30, 10))
        
        def guardar():
            if es_edicion:
                nombre = nombre_tarea
            else:
                nombre = entry_nombre.get().strip()
                if not nombre:
                    messagebox.showerror("Error", "Debes ingresar un nombre")
                    return
            
            frecuencia = var_frecuencia.get()
            
            dias_selec = []
            if frecuencia == "WEEKLY":
                for corto, var in dias_vars.items():
                    if var.get():
                        dias_selec.append(self.dias_map[corto])
                
                if not dias_selec:
                    messagebox.showerror("Error", "Debes seleccionar al menos un día para tarea semanal")
                    return
            
            hora = entry_hora.get().strip()
            minuto = entry_minuto.get().strip()
            
            if not hora or not minuto:
                messagebox.showerror("Error", "Debes ingresar hora y minuto")
                return
            
            if not hora.isdigit() or not minuto.isdigit():
                messagebox.showerror("Error", "Hora y minuto deben ser números")
                return
            
            hora_int = int(hora)
            minuto_int = int(minuto)
            
            if hora_int < 0 or hora_int > 23:
                messagebox.showerror("Error", "La hora debe estar entre 00 y 23")
                return
            
            if minuto_int < 0 or minuto_int > 59:
                messagebox.showerror("Error", "Los minutos deben estar entre 00 y 59")
                return
            
            horario = f"{hora_int:02d}:{minuto_int:02d}"
            
            ahora = datetime.now()
            hora_tarea = datetime.now().replace(hour=hora_int, minute=minuto_int, second=0, microsecond=0)
            
            mostrar_aviso_hora = False
            
            if frecuencia == "DAILY" and hora_tarea <= ahora:
                mostrar_aviso_hora = True
                mensaje_aviso = f"⏰ Se programará para mañana a las {horario}"
            elif frecuencia == "WEEKLY":
                dias_semana_eng = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                dia_actual = dias_semana_eng[ahora.weekday()]
                
                if dia_actual in dias_selec and hora_tarea <= ahora:
                    dias_nombres = {'MON': 'Lunes', 'TUE': 'Martes', 'WED': 'Miércoles', 
                                   'THU': 'Jueves', 'FRI': 'Viernes', 'SAT': 'Sábado', 'SUN': 'Domingo'}
                    dia_nombre = dias_nombres.get(dia_actual, 'próximo día')
                    mostrar_aviso_hora = True
                    mensaje_aviso = f"⏰ Se ejecutará el próximo {dia_nombre} a las {horario}"
            
            if es_edicion:
                if nombre.startswith('\\'):
                    nombre = nombre[1:]
                
                if nombre.startswith(self.prefijo_tarea):
                    nombre_completo = nombre
                else:
                    nombre_completo = f"{self.prefijo_tarea}_{nombre}"
                
                subprocess.run(['schtasks', '/Delete', '/TN', nombre_completo, '/F'], capture_output=True)
            
            ventana.destroy()
            
            self._crear_tarea_windows(nombre, frecuencia, horario, dias_selec if frecuencia == "WEEKLY" else None, mostrar_aviso_hora)
            
            if mostrar_aviso_hora:
                self.root.after(100, lambda: self._mostrar_toast(mensaje_aviso, duracion=4000, color="#ffc107"))
        
        texto_boton = "💾 Guardar Cambios" if es_edicion else "✅ Crear Tarea"
        tk.Button(
            frame_btns,
            text=texto_boton,
            font=("Segoe UI", 10, "bold"),
            bg="#28a745",
            fg="white",
            width=18,
            command=guardar
        ).pack(side='right', padx=(10, 30))

    def _crear_tarea_windows(self, nombre, frecuencia, horario, dias=None, ya_mostro_aviso=False):
        """Crea una tarea en el Programador de Tareas de Windows"""
        try:
            if not nombre.startswith(self.prefijo_tarea):
                nombre_completo = f"{self.prefijo_tarea}_{nombre}"
            else:
                nombre_completo = nombre
            
            directorio_trabajo = os.path.dirname(self.ruta_script)
            
            comando_tarea = f'cmd /c "cd /d "{directorio_trabajo}" && py "{self.ruta_script}""'
            
            comando = [
                'schtasks',
                '/Create',
                '/TN', nombre_completo,
                '/TR', comando_tarea,
                '/SC', frecuencia,
                '/ST', horario
            ]
            
            if frecuencia == 'WEEKLY' and dias:
                comando.extend(['/D', ','.join(dias)])
            
            comando.append('/F')
            
            resultado = subprocess.run(
                comando,
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                self._cargar_tareas()
                
                if not ya_mostro_aviso:
                    detalles = self._obtener_detalles_tarea(nombre_completo)
                    proxima = detalles.get('Hora próxima ejecución', 'próximamente')
                    
                    self._mostrar_toast(f"✅ Tarea programada para {proxima}")
            else:
                messagebox.showerror("❌ Error", f"No se pudo crear la tarea:\n{resultado.stderr}")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error creando tarea:\n{e}")

    def _eliminar_tarea(self):
        """Elimina la tarea seleccionada"""
        seleccion = self.tree.selection()
        
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona una tarea para eliminar")
            return
        
        item = self.tree.item(seleccion[0])
        nombre_tarea = item['values'][0]
        
        if nombre_tarea == 'No hay tareas programadas':
            return
        
        if nombre_tarea.startswith('\\'):
            nombre_tarea = nombre_tarea[1:]
        
        respuesta = messagebox.askyesno(
            "Confirmar",
            f"¿Eliminar la tarea '{nombre_tarea}'?"
        )
        
        if not respuesta:
            return
        
        try:
            if nombre_tarea.startswith(self.prefijo_tarea):
                nombre_completo = nombre_tarea
            else:
                nombre_completo = f"{self.prefijo_tarea}_{nombre_tarea}"
            
            resultado = subprocess.run(
                ['schtasks', '/Delete', '/TN', nombre_completo, '/F'],
                capture_output=True,
                text=True
            )
            
            if resultado.returncode == 0:
                self._cargar_tareas()
                self._mostrar_toast(f"✅ Tarea eliminada correctamente")
            else:
                messagebox.showerror("❌ Error", f"No se pudo eliminar la tarea")
        
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error eliminando tarea:\n{e}")

    def ejecutar(self):
        """Inicia la interfaz"""
        self.root.mainloop()


def main():
    gestor = GestorTareasGUI()
    gestor.ejecutar()


if __name__ == "__main__":
    main()