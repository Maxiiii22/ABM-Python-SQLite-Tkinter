import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk # Para crear una tabla.
import sqlite3
import sys
import os

# --- Seccion Funciones usadas regularmente ---

# Función para cargar los datos de la base de datos en la tabla : 
def mostrar_registros(*args):  # Al usar el metodo trace_add() debemos  usar *args . Ya que trace_add pasará tres argumentos (name, index y mode)
        
    filtro = variable_filtro.get().strip()
    opcion = opciones_combobox.get()  
    
    consulta = "SELECT * FROM empleados"
    parametro = ()

    
    if filtro:
        if opcion == 'Nombre':
            consulta += " WHERE nombre LIKE ?"  
            parametro = (f'%{filtro}%',)  
        elif opcion == 'Apellido':
            consulta += " WHERE apellido LIKE ?"
            parametro = (f'%{filtro}%',)
        elif opcion == 'Edad':
            consulta += " WHERE edad LIKE ?"
            parametro = (f'%{filtro}%',)
        elif opcion == 'Id': 
            consulta += " WHERE id = ?"
            parametro = (filtro,)    
    
    c.execute(consulta, parametro)
    filas = c.fetchall()
    
    # Limpiar los datos existentes en la tabla
    for fila in tabla.get_children():
        tabla.delete(fila)
    
    # Insertar los nuevos datos
    for fila in filas:
        tabla.insert("", tk.END, values=fila)


def obtener_ultimo_id():
    c.execute("SELECT MAX(id) FROM empleados")
    ultimo_id = c.fetchone()[0]
    if ultimo_id is None:
        siguiente_id = 1
    else:
        siguiente_id = ultimo_id + 1
    
    entry_id.configure(state="normal") 
    entry_id.delete(0,tk.END) #Limpio
    entry_id.insert(0,siguiente_id) # Y pongo el ultimo id + 1.
    entry_id.configure(state="disabled") 

def limpiar_campos():
    entry_id.configure(state="normal")
    entry_nombre.configure(state="normal")  
    entry_apellido.configure(state="normal")
    entry_edad.configure(state="normal")
    entry_id.delete(0,tk.END) 
    entry_nombre.delete(0,tk.END)
    entry_apellido.delete(0,tk.END)
    entry_edad.delete(0,tk.END)

# ---- Fin Seccion Funciones ----


# --- Seccion de Alta ---
def agregar_empleado():
    empleado_nombre = entry_nombre.get()
    empleado_apellido = entry_apellido.get()
    empleado_edad = entry_edad.get()
    
    if not empleado_nombre or not empleado_edad or not empleado_apellido :
        messagebox.showwarning("Advertencia","Por favor, complete todos los campos.")  
        return
    try:
        empleado_edad = int(empleado_edad)  
    except ValueError: 
        messagebox.showwarning("Advertencia","El campo Edad deben ser numeros.")
        return
    
    try:
        c.execute(
            """
            INSERT INTO empleados
            (nombre,apellido,edad) VALUES (?,?,?) """,
            (empleado_nombre,empleado_apellido,empleado_edad)
        )
        conexion.commit() 
        
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Hubo un problema al agregar al empleado: {e}")
        return
    
    obtener_ultimo_id()
    entry_nombre.delete(0,tk.END)
    entry_apellido.delete(0,tk.END)
    entry_edad.delete(0,tk.END)
    entry_nombre.focus_set()
    mostrar_registros() # Limpia y muestra los registros en la tabla.
    messagebox.showinfo("¡Éxito!","El empleado se agrego correctamente.")    



def btnAlta():
    label_opcion.configure(text="Alta de Empleado")
    limpiar_campos()
    obtener_ultimo_id()  
    entry_nombre.configure(state="normal")   
    entry_nombre.focus_set() 
    entry_apellido.configure(state="normal")
    entry_edad.configure(state="normal")
    btn_accion.configure(state="normal", command=agregar_empleado,text="Agregar")
    btn_baja.configure(text="Baja de Empleado")
    btn_modificacion.configure(text="Modificacion de Empleado")

# ---- Fin seccion Alta ----

# --- Seccion Modificacion ---

def modificar_empleado(empleado_id):
    empleado_nombre = entry_nombre.get()
    empleado_apellido = entry_apellido.get()
    empleado_edad = entry_edad.get() 
    
    if not empleado_nombre or not empleado_edad or not empleado_apellido :
        messagebox.showwarning("Advertencia","Por favor, complete todos los campos.")  
        return
    try:
        empleado_edad = int(empleado_edad)
    except ValueError:  
        messagebox.showwarning("Advertencia","El campo Edad deben ser numeros.")
        return
    try:
        c.execute(
            """
            UPDATE empleados set nombre = ? , apellido = ? , edad = ? 
            WHERE id = ?""",(empleado_nombre, empleado_apellido, empleado_edad, empleado_id)
        )
        conexion.commit()
    
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Hubo un problema al modificar al empleado: {e}")
        return
    
    btn_accion.configure(text="Buscar...")
    btn_modificacion.configure(text="Modificacion de Empleado")
    mostrar_registros() 
    limpiar_campos()
    entry_nombre.configure(state="disabled")
    entry_apellido.configure(state="disabled")
    entry_edad.configure(state="disabled")   
    messagebox.showinfo("¡Éxito!","El empleado se modifico correctamente.")



def dar_modificacion():
    identificador = entry_id.get()
    if not identificador :
        messagebox.showwarning("Advertencia","Por favor, Ingrese el ID del empleado a Modificar.")  
        return
    try:
        identificador = int(identificador) 
    except ValueError: 
        messagebox.showwarning("Advertencia","El campo ID deben ser numeros.")
        return    
    
    try:
        c.execute("SELECT * FROM empleados WHERE id = ?",(identificador,) )
        registro_empleado = c.fetchone()
        if registro_empleado:
            empleado_nombre = registro_empleado[1]   
            empleado_apellido = registro_empleado[2]
            empleado_edad = registro_empleado[3]   
            
            entry_id.configure(state="disabled")
            entry_nombre.configure(state="normal")
            entry_apellido.configure(state="normal")
            entry_edad.configure(state="normal")
            entry_nombre.insert(0,empleado_nombre)
            entry_apellido.insert(0,empleado_apellido)
            entry_edad.insert(0,empleado_edad)
            btn_modificacion.configure(text="Limpiar campos")
            btn_accion.configure(text="Modificar", command= lambda : modificar_empleado(identificador))
        else:
            messagebox.showerror("Error", "Empleado no existente.")
        
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error en la base de datos: {e}")


def btnModificacion():
    label_opcion.configure(text="Modificación de Empleado")
    limpiar_campos()
    entry_id.focus_set()  
    entry_nombre.configure(state="disabled")   
    entry_apellido.configure(state="disabled")
    entry_edad.configure(state="disabled")
    btn_baja.configure(text="Baja de Empleado")
    btn_modificacion.configure(text="Modificacion de Empleado")
    btn_accion.configure(state="normal", command= dar_modificacion, text="Buscar...")

# ---- Fin Seccion Modificacion ----


# --- Seccion Baja ---

def eliminar_empleado(empleado_id):
    try:
        c.execute(
            "DELETE FROM empleados WHERE id = ?",(empleado_id,)
        )
        conexion.commit()
        c.execute(
            ' DELETE FROM sqlite_sequence WHERE name="empleados" '   # Reinicio el auto-increment.
        )
        conexion.commit()  
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Hubo un problema al eliminar el empleado: {e}")
        return
    
    btn_accion.configure(text="Buscar...")
    btn_baja.configure(text="Baja de Empleado")
    mostrar_registros() # Limpia y muestra los registros en la tabla.
    limpiar_campos()
    messagebox.showinfo("¡Éxito!","El empleado se elimino correctamente.")



def dar_baja():
    identificador = entry_id.get()
    if not identificador :
        messagebox.showwarning("Advertencia","Por favor, Ingrese el ID del empleado a eliminar.")  
        return
    try:
        identificador = int(identificador)  
    except ValueError:  
        messagebox.showwarning("Advertencia","El campo ID deben ser numeros.")
        return    
    
    try:
        c.execute("SELECT * FROM empleados WHERE id = ?",(identificador,) )
        registro_empleado = c.fetchone()
        if registro_empleado:
            empleado_nombre = registro_empleado[1]   
            empleado_apellido = registro_empleado[2]
            empleado_edad = registro_empleado[3]   
            
            entry_id.configure(state="disabled")
            entry_nombre.configure(state="normal")
            entry_apellido.configure(state="normal")
            entry_edad.configure(state="normal")
            entry_nombre.insert(0,empleado_nombre)
            entry_apellido.insert(0,empleado_apellido)
            entry_edad.insert(0,empleado_edad)
            entry_nombre.configure(state="disabled")
            entry_apellido.configure(state="disabled")
            entry_edad.configure(state="disabled")
            btn_baja.configure(text="Limpiar campos")
            btn_accion.configure(text="Eliminar", command= lambda : eliminar_empleado(identificador))
        else:
            messagebox.showerror("Error", "Empleado no existente.")
    except sqlite3.Error as e:
        messagebox.showerror("Error", f"Error en la base de datos: {e}")


def btnBaja():
    label_opcion.configure(text="Baja de Empleado")
    limpiar_campos()
    entry_id.focus_set() 
    entry_nombre.configure(state="disabled")   
    entry_apellido.configure(state="disabled")
    entry_edad.configure(state="disabled")
    btn_modificacion.configure(text="Modificacion de Empleado")
    btn_baja.configure(text="Baja de Empleado")
    btn_accion.configure(state="normal", command= dar_baja, text="Buscar...")


# ---- Fin Seccion Baja ----


# --- Comienzo principal:  ----

#Este código asegura que, ya sea que estés ejecutando el script desde un entorno de desarrollo o desde un ejecutable empaquetado, el archivo de base de datos se pueda localizar correctamente y 
# establecer la conexión adecuada:
def get_db_path(): #Se encargará de determinar la ruta al archivo de base de datos.
    if getattr(sys, 'frozen', False):  #Verifica si el atributo 'frozen' está presente en el objeto sys. Este atributo es añadido por PyInstaller cuando el script se ejecuta como un ejecutable empaquetado. Si 'frozen' está presente, significa que el script se está ejecutando desde un ejecutable generado por PyInstaller.
        #Si el script se está ejecutando como un ejecutable empaquetado, sys._MEIPASS es el directorio temporal donde PyInstaller extrae los archivos incluidos en el ejecutable. 
        # Se usa este directorio para construir la ruta al archivo de base de datos.
        base_path = sys._MEIPASS
    else:
        #Si el atributo 'frozen' no está presente, significa que el script se está ejecutando en un entorno de desarrollo
        # __file__ es la ruta al archivo del script Python actual. 
        base_path = os.path.dirname(__file__) #obtiene el directorio donde se encuentra el archivo del script, que es donde esperamos que esté el archivo de base de datos.
    
    return os.path.join(base_path, 'Bd_Empleados.db') # Une base_path con el nombre del archivo de base de datos ('Bd_Empleados.db') para construir la ruta completa al archivo de base de datos. Esta ruta es devuelta por la función get_db_path.

db_path = get_db_path()

#Todo eso de arriba es para evitar errores de la ruta de la BD , por si creamos un ejecutable y lo llevamos a otra pc.
conexion = sqlite3.connect(db_path)
if conexion :
    c = conexion.cursor()  
    c.execute(
    """
        CREATE TABLE IF NOT EXISTS empleados(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            edad INTEGER NOT NULL
        )      
    """)
    conexion.commit()  

    root = ctk.CTk()
    root.title("Gestion de Empleados")
    root.resizable(False,False)
    root.geometry("+500+300")

    estilo = {"font":("Arial",15,"bold"), "width":200} 

    labelFrame = ctk.CTkFrame(root)
    
    btn_alta = ctk.CTkButton(labelFrame, command=btnAlta, text="Alta de Empleado", fg_color="green", hover_color="dark green",**estilo ) 
    btn_modificacion = ctk.CTkButton(labelFrame, command=btnModificacion, text="Modificacion de Empleado", fg_color="blue",hover_color="blue4", **estilo) 
    btn_baja = ctk.CTkButton(labelFrame, command=btnBaja, text="Baja de Empleado", fg_color="red", hover_color="red4",**estilo)
    
    labelFrame.grid(row=0, column=0, columnspan="2", rowspan="6")
    btn_alta.grid(row=0, column=0, pady=(50,10))
    btn_modificacion.grid(row=1, column=0, pady=30, padx=10)
    btn_baja.grid(row=2, column=0, pady=(10,50))

    label_opcion = ctk.CTkLabel(root, text="Elija una opción", font=("Arial",20,"bold"), width=300)
    
    label_id = ctk.CTkLabel(root,text="ID")
    entry_id = ctk.CTkEntry(root,state="disabled")
    
    label_nombre = ctk.CTkLabel(root,text="Nombre")
    entry_nombre = ctk.CTkEntry(root,state="disabled")
    
    label_apellido = ctk.CTkLabel(root,text="Apellido")
    entry_apellido = ctk.CTkEntry(root,state="disabled")
    
    label_edad = ctk.CTkLabel(root,text="Edad")
    entry_edad = ctk.CTkEntry(root,state="disabled")
    
    btn_accion = ctk.CTkButton(root,text="Agregar", state="disabled")

    padding_entry: dict = {"padx":(0,20)}

    label_opcion.grid(row=0,column=2, columnspan="2")
    
    label_id.grid(row=1,column=2, padx=20)
    entry_id.grid(row=1,column=3, **padding_entry)
    
    label_nombre.grid(row=2,column=2, padx=20)
    entry_nombre.grid(row=2,column=3, **padding_entry)
    
    label_apellido.grid(row=3,column=2, padx=20)
    entry_apellido.grid(row=3,column=3, **padding_entry)
    
    label_edad.grid(row=4,column=2, padx=20)
    entry_edad.grid(row=4,column=3, **padding_entry)
    
    btn_accion.grid(row=5,column=2, columnspan="2")

    label_filtrar = ctk.CTkLabel(root, text="Filtrar por:", font=("Arial",20,"bold"))
    label_filtrar.grid(row=0,column=4, sticky="w", padx=(20,0))  

    opciones_combobox =  ctk.CTkComboBox(root, values=["Id", "Nombre", "Apellido", "Edad"], width=85)
    opciones_combobox.grid(row=0, column=4, padx=(0,75) )
    opciones_combobox.set("Id")  

    variable_filtro = ctk.StringVar()
    entry_filtro = ctk.CTkEntry(root, textvariable= variable_filtro, width=177)
    entry_filtro.grid(row=0, column=4, sticky="e", padx=(0,20))
    

    variable_filtro.trace_add("write", mostrar_registros)  # Cada vez que se escriba o borre en el entry se llamara a la funcion mostrar_registros() 
    opciones_combobox.bind("<FocusOut>", lambda e: mostrar_registros()) # El evento FocusOut llama la funcion , cuando se deja de hacer focus en el.


    # Crear el Treeview (tabla) :
    columnas = ("ID","Nombre","Apellido","Edad")  # Define los nombres de las columnas.
    tabla = ttk.Treeview(root,  # ttk.Treeview : Este widget permite mostrar datos en una estructura tabular, similar a una tabla de una hoja de cálculo.
                        columns= columnas, # El columns se usa para poner los encabezados.
                        show="headings" # La opción show controla qué partes del Treeview deben ser visibles. Aquí, se establece en "headings", lo que significa que solo se mostrarán los encabezados de las columnas.
                        )

    for campo in columnas:
        tabla.heading(campo, text=campo) # Establece el texto del encabezado de la columna
        tabla.column(campo, width=100)  # Establece el ancho de la columna

    tabla.grid(row=1, column=4, rowspan="6", padx=(0,10))
    mostrar_registros() # Limpia y muestra los registros en la tabla.
    
    root.mainloop()
    
else:
    print("Error en la conexion a la Base de Datos...")
