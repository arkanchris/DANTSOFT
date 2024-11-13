import tkinter as tk
from tkinter import messagebox, ttk
from tkinter.font import Font
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
import os

# Función para eliminar la base de datos si no deseas conservar los datos existentes
def eliminar_db():
    if os.path.exists("clientes.db"):
        os.remove("clientes.db")
        print("Base de datos eliminada.")
    else:
        print("No se encontró la base de datos.")

# Función para modificar la base de datos y agregar la columna 'plataforma' si no existe
def modificar_db():
    try:
        conn = sqlite3.connect("clientes.db")
        cursor = conn.cursor()
        
        # Agregar la columna 'plataforma' si no existe
        cursor.execute("ALTER TABLE clientes ADD COLUMN plataforma TEXT")
        
        conn.commit()
        conn.close()
        print("Columna 'plataforma' añadida correctamente.")
    except Exception as e:
        print(f"Error al modificar la base de datos: {e}")

# Función para conectar a la base de datos y crear la tabla si no existe
def conectar_db():
    conn = sqlite3.connect("clientes.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            perfil TEXT NOT NULL,
            telefono TEXT NOT NULL,
            proveedor TEXT NOT NULL,
            orden TEXT,
            correo TEXT NOT NULL,
            contrasena TEXT,
            pin TEXT,
            precio REAL NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            plataforma TEXT  -- Asegurarse de que la columna 'plataforma' esté presente
        )
    ''')
    conn.commit()
    conn.close()

# Función para agregar un cliente a la base de datos
def agregar_cliente():
    # Obtener valores de los campos
    cliente = entries[0].get()
    perfil = entries[1].get()
    telefono = entries[2].get()
    proveedor = entries[3].get()
    orden = entries[4].get()
    correo = entries[5].get()
    contrasena = entries[6].get()
    pin = entries[7].get()
    precio = entries[8].get()
    plataforma = combobox_plataforma.get()
    fecha_inicio = entry_fecha_inicio.get_date().strftime('%Y-%m-%d')
    fecha_fin = entry_fecha_fin.get_date().strftime('%Y-%m-%d')

    # Verificación de que todos los campos obligatorios estén completos
    if not all([cliente, perfil, telefono, proveedor, correo, precio, fecha_inicio, fecha_fin, plataforma]):
        messagebox.showwarning("Advertencia", "Por favor, llena todos los campos obligatorios.")
        return

    try:
        # Conectar a la base de datos y guardar el cliente
        conn = sqlite3.connect("clientes.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (cliente, perfil, telefono, proveedor, orden, correo, contrasena, pin, precio, fecha_inicio, fecha_fin, plataforma)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cliente, perfil, telefono, proveedor, orden, correo, contrasena, pin, float(precio), fecha_inicio, fecha_fin, plataforma))
        conn.commit()
        conn.close()

        # Confirmación y limpieza de campos
        messagebox.showinfo("Registro exitoso", "El cliente ha sido registrado correctamente.")
        limpiar_campos()

    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar cliente: {e}")

# Función para limpiar los campos después del registro
def limpiar_campos():
    for entry in entries:
        entry.delete(0, tk.END)
        entry.insert(0, entry.placeholder)
    combobox_plataforma.set('')  # Limpiar la selección de la plataforma

def ver_clientes():
    # Crear una nueva ventana para la consulta de clientes
    ventana_consulta = tk.Toplevel(ventana)
    ventana_consulta.title("Consulta de Clientes")
    ventana_consulta.geometry("400x100")
    ventana_consulta.config(bg="#f0f0f0")  # Fondo igual al de la ventana principal
    
    # Crear un Label y un Combobox para seleccionar la plataforma
    label_plataforma_filtro = tk.Label(ventana_consulta, text="Selecciona Plataforma:", bg="#f0f0f0", font=font_style)
    label_plataforma_filtro.grid(row=0, column=0, padx=5, pady=5, sticky="e")
    combobox_plataforma_filtro = ttk.Combobox(ventana_consulta, values=plataformas, font=font_style, state="readonly")
    combobox_plataforma_filtro.grid(row=0, column=1, padx=5, pady=5)

    # Función para obtener los clientes filtrados
    def obtener_clientes():
        plataforma_seleccionada = combobox_plataforma_filtro.get()
        
        # Limpiar la tabla si existe una previamente
        for item in tabla.get_children():
            tabla.delete(item)
        
        # Conectar a la base de datos y obtener los clientes filtrados por plataforma
        conn = sqlite3.connect("clientes.db")
        cursor = conn.cursor()
        
        # Si se selecciona una plataforma, filtrar por esa plataforma
        if plataforma_seleccionada:
            cursor.execute("SELECT cliente, perfil, telefono, proveedor, orden, correo, fecha_inicio, fecha_fin, plataforma FROM clientes WHERE plataforma = ?", (plataforma_seleccionada,))
        else:
            cursor.execute("SELECT cliente, perfil, telefono, proveedor, orden, correo, fecha_inicio, fecha_fin, plataforma FROM clientes")
        
        registros = cursor.fetchall()
        conn.close()

        # Crear la tabla de clientes
        columnas = ("Cliente", "Perfil", "Teléfono", "Proveedor", "Orden", "Correo", "Fecha Inicio", "Fecha Fin", "Plataforma")
        tabla = ttk.Treeview(ventana_consulta, columns=columnas, show="headings")

        # Establecer los encabezados de las columnas
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, width=120, anchor="center")  # Alineación y tamaño de columnas

        # Insertar registros en la tabla
        for registro in registros:
            tabla.insert("", tk.END, values=registro)

        # Estilo de la tabla
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=("Dosis ExtraBold", 11),
                        foreground="black", background="#ecf0f1",  # Fondo de celdas más claro
                        fieldbackground="#ecf0f1", rowheight=25)

        style.map("Custom.Treeview", background=[("selected", "#4CAF50")])  # Color de fila seleccionada

        tabla.configure(style="Custom.Treeview")  # Aplicar el estilo a la tabla
        tabla.pack(expand=True, fill="both", padx=10, pady=10)

    # Crear un botón para obtener los clientes filtrados
    boton_consultar = tk.Button(ventana_consulta, text="Consultar", command=obtener_clientes, font=font_style, bg="blue", fg="white")
    boton_consultar.grid(row=1, column=0, columnspan=2, padx=10, pady=10)



# Configuración de la ventana principal
ventana = tk.Tk()
ventana.title("Gestión de Clientes de Streaming")
ventana.geometry("600x350")
ventana.config(bg="#f0f0f0")

# Cargar fuente personalizada
font_style = Font(family="Dosis ExtraBold", size=11)

# Estilos de ttk para bordes redondeados
style = ttk.Style()
style.configure("Rounded.TEntry", font=font_style, foreground="grey", fieldbackground="white", borderwidth=5)
style.layout("Rounded.TEntry", [("Entry.border", {"sticky": "nswe", "children": [("Entry.padding", {"sticky": "nswe", "children": [("Entry.textarea", {"sticky": "nswe"})]})]})])

# Funciones para el marcador de posición
def on_focus_in(entry):
    if entry.get() == entry.placeholder:
        entry.delete(0, tk.END)
        entry.config(foreground="black")

def on_focus_out(entry):
    if entry.get() == "":
        entry.insert(0, entry.placeholder)
        entry.config(foreground="grey")

# Configuración de campos y marcadores de posición
campos = [
    ("Cliente:", "Nombre completo"),
    ("Perfil:", "Perfil de usuario"),
    ("Teléfono:", "Número de teléfono"),
    ("Proveedor:", "Nombre del proveedor"),
    ("Orden:", "Número de orden"),
    ("Correo:", "Correo electrónico"),
    ("Contraseña:", "Contraseña"),
    ("Pin:", "PIN"),
    ("Precio:", "Precio en USD")
]

entries = []

# Crear entradas con marcador de posición
def crear_entry(row, col, placeholder):
    entry = ttk.Entry(ventana, width=20, font=font_style, style="Rounded.TEntry")
    entry.insert(0, placeholder)
    entry.placeholder = placeholder
    entry.bind("<FocusIn>", lambda event, e=entry: on_focus_in(e))
    entry.bind("<FocusOut>", lambda event, e=entry: on_focus_out(e))
    entry.grid(row=row, column=col, padx=5, pady=5)
    return entry

# Crear etiquetas y entradas en una cuadrícula
for i, (label_text, placeholder) in enumerate(campos):
    row, col = divmod(i, 2)
    label = tk.Label(ventana, text=label_text, bg="#f0f0f0", font=font_style)
    label.grid(row=row, column=col * 2, padx=5, pady=5, sticky="e")
    entry = crear_entry(row, col * 2 + 1, placeholder)
    entries.append(entry)

# Campos de fecha con calendario
label_fecha_inicio = tk.Label(ventana, text="Fecha Inicio:", bg="#f0f0f0", font=font_style)
label_fecha_inicio.grid(row=5, column=0, padx=5, pady=5, sticky="e")
entry_fecha_inicio = DateEntry(ventana, width=18, font=font_style, background='darkblue', foreground='white', borderwidth=2)
entry_fecha_inicio.grid(row=5, column=1, padx=5, pady=5)

label_fecha_fin = tk.Label(ventana, text="Fecha Fin:", bg="#f0f0f0", font=font_style)
label_fecha_fin.grid(row=5, column=2, padx=5, pady=5, sticky="e")
entry_fecha_fin = DateEntry(ventana, width=18, font=font_style, background='darkblue', foreground='white', borderwidth=2)
entry_fecha_fin.grid(row=5, column=3, padx=5, pady=5)

# Combobox para la plataforma
label_plataforma = tk.Label(ventana, text="Plataforma:", bg="#f0f0f0", font=font_style)
label_plataforma.grid(row=6, column=0, padx=5, pady=5, sticky="e")
plataformas = ['Netflix', 'HBO', 'Prime Video', 'Disney+', 'VIX', 'Plex', 'Spotify', 'Youtube', 'Paramount', 'Crunchyroll']
combobox_plataforma = ttk.Combobox(ventana, values=plataformas, font=font_style, state="readonly")
combobox_plataforma.grid(row=6, column=1, padx=5, pady=5)

# Botones
boton_guardar = tk.Button(ventana, text="Guardar Cliente", command=agregar_cliente, font=font_style, bg="green", fg="white")
boton_guardar.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

boton_ver_clientes = tk.Button(ventana, text="Ver Clientes", command=ver_clientes, font=font_style, bg="blue", fg="white")
boton_ver_clientes.grid(row=7, column=2, columnspan=2, padx=10, pady=10)

# Crear la base de datos y modificarla si es necesario
modificar_db()  # Llama a modificar_db para asegurarte de que la columna 'plataforma' esté añadida

# Iniciar la ventana
ventana.mainloop()
