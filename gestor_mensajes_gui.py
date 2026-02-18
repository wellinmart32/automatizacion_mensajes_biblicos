import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class GestorMensajesGUI:
    """Interfaz gráfica para gestionar mensajes bíblicos (.txt)"""

    def __init__(self):
        self.carpeta_mensajes = "mensajes"

        self.root = tk.Tk()
        self.root.title("📝 Gestor de Mensajes Bíblicos")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
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

        self._construir_ui()
        self._cargar_mensajes()

    def _construir_ui(self):

        # Header
        header = tk.Frame(self.root, bg="#1a73e8", pady=12)
        header.pack(fill='x')
        tk.Label(
            header,
            text="📝 Gestor de Mensajes Bíblicos",
            font=("Segoe UI", 14, "bold"),
            bg="#1a73e8",
            fg="white"
        ).pack()

        # Panel principal dividido en 2
        panel = tk.Frame(self.root, bg="#f0f0f0")
        panel.pack(fill='both', expand=True, padx=10, pady=10)

        # ==================== PANEL IZQUIERDO (lista) ====================
        panel_izq = tk.Frame(panel, bg="#f0f0f0", width=250)
        panel_izq.pack(side='left', fill='y', padx=(0, 5))
        panel_izq.pack_propagate(False)

        tk.Label(
            panel_izq,
            text="📂 Mensajes disponibles",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        # Contador
        self.lbl_contador = tk.Label(
            panel_izq,
            text="0 mensajes",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_contador.pack(anchor='w', pady=(0, 5))

        # Lista con scrollbar
        frame_lista = tk.Frame(panel_izq, bg="#f0f0f0")
        frame_lista.pack(fill='both', expand=True)

        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side='right', fill='y')

        self.lista = tk.Listbox(
            frame_lista,
            yscrollcommand=scrollbar.set,
            font=("Segoe UI", 9),
            selectmode='single',
            bg="white",
            relief='solid',
            borderwidth=1
        )
        self.lista.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.lista.yview)

        self.lista.bind('<<ListboxSelect>>', self._on_seleccionar)

        # Botones de lista
        frame_btn_lista = tk.Frame(panel_izq, bg="#f0f0f0")
        frame_btn_lista.pack(fill='x', pady=(5, 0))

        tk.Button(
            frame_btn_lista,
            text="➕ Nuevo",
            font=("Segoe UI", 9, "bold"),
            bg="#1a73e8",
            fg="white",
            command=self._nuevo_mensaje
        ).pack(side='left', expand=True, fill='x', padx=(0, 2))

        tk.Button(
            frame_btn_lista,
            text="🗑️ Eliminar",
            font=("Segoe UI", 9),
            bg="#dc3545",
            fg="white",
            command=self._eliminar_mensaje
        ).pack(side='left', expand=True, fill='x', padx=(2, 0))

        # ==================== PANEL DERECHO (editor) ====================
        panel_der = tk.Frame(panel, bg="#f0f0f0")
        panel_der.pack(side='left', fill='both', expand=True)

        tk.Label(
            panel_der,
            text="✏️ Editor de mensaje",
            font=("Segoe UI", 10, "bold"),
            bg="#f0f0f0"
        ).pack(anchor='w', pady=(0, 5))

        # Nombre del archivo
        frame_nombre = tk.Frame(panel_der, bg="#f0f0f0")
        frame_nombre.pack(fill='x', pady=(0, 8))

        tk.Label(
            frame_nombre,
            text="Archivo:",
            font=("Segoe UI", 9),
            bg="#f0f0f0"
        ).pack(side='left')

        self.lbl_archivo = tk.Label(
            frame_nombre,
            text="(ninguno seleccionado)",
            font=("Segoe UI", 9, "italic"),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_archivo.pack(side='left', padx=5)

        # Área de texto
        frame_texto = tk.Frame(panel_der, bg="#f0f0f0")
        frame_texto.pack(fill='both', expand=True)

        scrollbar_texto = tk.Scrollbar(frame_texto)
        scrollbar_texto.pack(side='right', fill='y')

        self.texto = tk.Text(
            frame_texto,
            yscrollcommand=scrollbar_texto.set,
            font=("Segoe UI", 10),
            wrap='word',
            relief='solid',
            borderwidth=1,
            bg="white",
            padx=8,
            pady=8
        )
        self.texto.pack(fill='both', expand=True)
        scrollbar_texto.config(command=self.texto.yview)

        # Contador de caracteres
        self.lbl_chars = tk.Label(
            panel_der,
            text="0 caracteres",
            font=("Segoe UI", 8),
            fg="gray",
            bg="#f0f0f0"
        )
        self.lbl_chars.pack(anchor='e', pady=(2, 0))

        self.texto.bind('<KeyRelease>', self._actualizar_contador_chars)

        # Botones del editor
        frame_btn_editor = tk.Frame(panel_der, bg="#f0f0f0")
        frame_btn_editor.pack(fill='x', pady=(8, 0))

        tk.Button(
            frame_btn_editor,
            text="🗑️ Limpiar",
            font=("Segoe UI", 9),
            bg="#e0e0e0",
            command=self._limpiar_editor
        ).pack(side='left', padx=(0, 5))

        tk.Button(
            frame_btn_editor,
            text="💾 Guardar mensaje",
            font=("Segoe UI", 10, "bold"),
            bg="#1a73e8",
            fg="white",
            command=self._guardar_mensaje
        ).pack(side='right')

    def _cargar_mensajes(self):
        """Carga la lista de mensajes desde la carpeta"""
        self.lista.delete(0, tk.END)

        if not os.path.exists(self.carpeta_mensajes):
            os.makedirs(self.carpeta_mensajes)

        mensajes = sorted([
            f for f in os.listdir(self.carpeta_mensajes)
            if f.endswith('.txt')
        ])

        for mensaje in mensajes:
            self.lista.insert(tk.END, mensaje)

        self.lbl_contador.config(text=f"{len(mensajes)} mensajes")

    def _on_seleccionar(self, event):
        """Al seleccionar un mensaje de la lista lo muestra en el editor"""
        seleccion = self.lista.curselection()
        if not seleccion:
            return

        nombre = self.lista.get(seleccion[0])
        ruta = os.path.join(self.carpeta_mensajes, nombre)

        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                contenido = f.read()

            self.texto.delete('1.0', tk.END)
            self.texto.insert('1.0', contenido)
            self.lbl_archivo.config(text=nombre, fg="#1a73e8")
            self._actualizar_contador_chars()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al leer el mensaje: {e}")

    def _guardar_mensaje(self):
        """Guarda el contenido del editor en el archivo seleccionado"""
        nombre = self.lbl_archivo.cget('text')

        if nombre == "(ninguno seleccionado)":
            messagebox.showwarning("⚠️ Aviso", "Selecciona un mensaje o crea uno nuevo")
            return

        contenido = self.texto.get('1.0', tk.END).strip()

        if not contenido:
            messagebox.showwarning("⚠️ Aviso", "El mensaje no puede estar vacío")
            return

        ruta = os.path.join(self.carpeta_mensajes, nombre)

        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo("✅ Éxito", f"Mensaje guardado: {nombre}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al guardar: {e}")

    def _nuevo_mensaje(self):
        """Crea un nuevo archivo de mensaje"""
        # Calcular siguiente número
        mensajes_existentes = [
            f for f in os.listdir(self.carpeta_mensajes)
            if f.endswith('.txt')
        ] if os.path.exists(self.carpeta_mensajes) else []

        siguiente_num = len(mensajes_existentes) + 1
        nombre_sugerido = f"mensaje-{siguiente_num:03d}.txt"

        nombre = simpledialog.askstring(
            "Nuevo mensaje",
            "Nombre del archivo:",
            initialvalue=nombre_sugerido,
            parent=self.root
        )

        if not nombre:
            return

        if not nombre.endswith('.txt'):
            nombre += '.txt'

        ruta = os.path.join(self.carpeta_mensajes, nombre)

        if os.path.exists(ruta):
            messagebox.showwarning("⚠️ Aviso", f"Ya existe un archivo llamado {nombre}")
            return

        try:
            with open(ruta, 'w', encoding='utf-8') as f:
                f.write("")

            self._cargar_mensajes()

            # Seleccionar el nuevo archivo en la lista
            for i in range(self.lista.size()):
                if self.lista.get(i) == nombre:
                    self.lista.selection_clear(0, tk.END)
                    self.lista.selection_set(i)
                    self.lista.see(i)
                    self._on_seleccionar(None)
                    break

            self.texto.focus_set()

        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al crear el archivo: {e}")

    def _eliminar_mensaje(self):
        """Elimina el mensaje seleccionado"""
        seleccion = self.lista.curselection()
        if not seleccion:
            messagebox.showwarning("⚠️ Aviso", "Selecciona un mensaje para eliminar")
            return

        nombre = self.lista.get(seleccion[0])

        confirmar = messagebox.askyesno(
            "🗑️ Confirmar eliminación",
            f"¿Estás seguro de eliminar '{nombre}'?\n\nEsta acción no se puede deshacer."
        )

        if not confirmar:
            return

        ruta = os.path.join(self.carpeta_mensajes, nombre)

        try:
            os.remove(ruta)
            self._cargar_mensajes()
            self._limpiar_editor()
            messagebox.showinfo("✅ Éxito", f"Mensaje eliminado: {nombre}")
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar: {e}")

    def _limpiar_editor(self):
        """Limpia el editor"""
        self.texto.delete('1.0', tk.END)
        self.lbl_archivo.config(text="(ninguno seleccionado)", fg="gray")
        self.lista.selection_clear(0, tk.END)
        self._actualizar_contador_chars()

    def _actualizar_contador_chars(self, event=None):
        """Actualiza el contador de caracteres"""
        contenido = self.texto.get('1.0', tk.END).strip()
        self.lbl_chars.config(text=f"{len(contenido)} caracteres")

    def ejecutar(self):
        self.root.mainloop()


def main():
    app = GestorMensajesGUI()
    app.ejecutar()


if __name__ == "__main__":
    main()