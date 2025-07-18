import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Toma de Inventarios - Pedro Castillo")
        self.df = None
        self.archivo_actual = None
        self.indice_actual = None

        # === ESTILO GENERAL ===
        self.fuente = ("Courier New", 10)
        bg_color = "#cce7ff"
        btn_color = "#004080"
        btn_fg = "white"
        entry_bg = "#e6f0ff"
        list_bg = "#f0f8ff"

        self.root.configure(bg=bg_color)

        self.frame_izq = tk.Frame(root, padx=10, pady=10, bg=bg_color)
        self.frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.frame_der = tk.Frame(root, padx=10, pady=10, bg=bg_color)
        self.frame_der.pack(side=tk.RIGHT, fill=tk.Y)

        # === BOTONES IZQUIERDA ===
        tk.Button(self.frame_izq, text="Cargar CSV", font=self.fuente, bg=btn_color, fg=btn_fg,
                  relief="raised", bd=3, command=self.cargar_csv).pack(pady=5, fill=tk.X)

        tk.Button(self.frame_izq, text="Guardar CSV", font=self.fuente, bg=btn_color, fg=btn_fg,
                  relief="raised", bd=3, command=self.guardar_csv).pack(pady=5, fill=tk.X)

        # === ETIQUETA DE ÚLTIMO PRODUCTO MODIFICADO ===
        self.texto_ultimo = tk.StringVar()
        self.texto_ultimo.set("Último producto modificado: Ninguno")
        tk.Label(self.frame_izq, textvariable=self.texto_ultimo, font=self.fuente,
                 bg="#d1ecf1", fg="#004085", relief="groove", bd=2, padx=5, pady=5).pack(pady=5, fill=tk.X)

        self.lista_resultados = tk.Listbox(self.frame_izq, height=15, width=60, font=self.fuente,
                                           bg=list_bg, bd=2, relief="sunken")
        self.lista_resultados.pack(pady=5)
        self.lista_resultados.bind('<<ListboxSelect>>', self.mostrar_detalles)

        self.texto_detalle = tk.StringVar()
        self.label_detalle = tk.Label(self.frame_izq, textvariable=self.texto_detalle,
                                      justify="left", anchor="w", bg=bg_color, font=self.fuente)
        self.label_detalle.pack(pady=5, fill=tk.X)

        self.entrada_cantidad = tk.Entry(self.frame_izq, font=self.fuente, bg=entry_bg, bd=2, relief="sunken")
        self.entrada_cantidad.pack(pady=5)

        frame_botones_cantidad = tk.Frame(self.frame_izq, bg=bg_color)
        frame_botones_cantidad.pack(pady=5)

        tk.Button(frame_botones_cantidad, text="Sumar Cantidad", font=self.fuente,
                  bg=btn_color, fg=btn_fg, relief="raised", bd=3,
                  command=self.sumar_cantidad).pack(side=tk.LEFT, padx=5)

        tk.Button(frame_botones_cantidad, text="Actualizar Cantidad", font=self.fuente,
                  bg=btn_color, fg=btn_fg, relief="raised", bd=3,
                  command=self.actualizar_cantidad).pack(side=tk.LEFT, padx=5)

        # === BÚSQUEDA DERECHA ===
        tk.Label(self.frame_der, text="Buscar producto:", bg=bg_color, font=self.fuente).pack()
        self.entrada_busqueda = tk.Entry(self.frame_der, font=self.fuente, bg=entry_bg, bd=2, relief="sunken")
        self.entrada_busqueda.pack()
        self.entrada_busqueda.bind('<KeyRelease>', self.buscar_producto)
        self.entrada_busqueda.bind('<Return>', self.seleccionar_primer_resultado)

        tk.Button(self.frame_der, text="Agregar nuevo producto", font=self.fuente,
                  bg="#0073e6", fg="white", relief="raised", bd=3,
                  command=self.abrir_formulario_producto).pack(pady=10)

        self.cargar_csv_inicio()

    def cargar_csv_inicio(self):
        posibles = [f for f in os.listdir() if f.endswith(".csv")]
        if posibles:
            self.archivo_actual = posibles[0]
            try:
                self.df = pd.read_csv(self.archivo_actual, encoding='latin1')
                messagebox.showinfo("Carga automática", f"Archivo '{self.archivo_actual}' cargado.")
                self.lista_resultados.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error al cargar CSV", str(e))

    def cargar_csv(self):
        archivo = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if archivo:
            try:
                self.df = pd.read_csv(archivo, encoding='latin1')
                self.archivo_actual = archivo
                self.lista_resultados.delete(0, tk.END)
                messagebox.showinfo("Carga exitosa", "Archivo CSV cargado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo: {e}")

    def guardar_csv(self):
        if self.df is None:
            return
        if not self.archivo_actual:
            self.archivo_actual = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if self.archivo_actual:
            try:
                self.df.to_csv(self.archivo_actual, index=False, encoding='latin1')
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def buscar_producto(self, event=None):
        if self.df is None:
            return
        query = self.entrada_busqueda.get().lower()
        resultados = self.df[self.df.iloc[:,1].astype(str).str.lower().str.contains(query)]
        self.lista_resultados.delete(0, tk.END)
        for i, row in resultados.iterrows():
            self.lista_resultados.insert(tk.END, f"{i} - {row[1]}")

    def seleccionar_primer_resultado(self, event=None):
        if self.lista_resultados.size() > 0:
            self.lista_resultados.selection_clear(0, tk.END)
            self.lista_resultados.selection_set(0)
            self.lista_resultados.activate(0)
            self.mostrar_detalles()

            try:
                actual = int(self.df.at[self.indice_actual, self.df.columns[3]])
                nuevo_valor = actual + 1
                self.df.at[self.indice_actual, self.df.columns[3]] = nuevo_valor
                self.guardar_csv()
                fila = self.df.loc[self.indice_actual]
                self.actualizar_ultimo_producto(fila)
            except Exception as e:
                messagebox.showerror("Error al sumar", str(e))

            self.lista_resultados.delete(0, tk.END)
            self.texto_detalle.set("")
            self.entrada_busqueda.focus_set()
            self.entrada_busqueda.select_range(0, tk.END)


    def mostrar_detalles(self, event=None):
        if not self.lista_resultados.curselection():
            return
        try:
            idx = int(self.lista_resultados.get(self.lista_resultados.curselection()).split(' - ')[0])
            self.indice_actual = idx
            fila = self.df.loc[idx]
            self.texto_detalle.set(
                f"Código: {fila[0]}\nProducto: {fila[1]}\nAtributo: {fila[2]}"
                f"\nCantidad Total: {fila[3]}\nCantidad Teórica: {fila[4]}"
            )
            self.entrada_cantidad.delete(0, tk.END)
            self.entrada_cantidad.insert(0, str(fila[3]))
        except Exception as e:
            messagebox.showerror("Error al mostrar detalles", str(e))

    def actualizar_cantidad(self):
        if self.df is None or self.indice_actual is None:
            return
        nueva_cantidad = self.entrada_cantidad.get()
        try:
            self.df.at[self.indice_actual, self.df.columns[3]] = int(nueva_cantidad)
            self.guardar_csv()
            self.mostrar_detalles()
            fila = self.df.loc[self.indice_actual]
            self.actualizar_ultimo_producto(fila)
            self.entrada_busqueda.focus_set()
            self.entrada_busqueda.select_range(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Cantidad inválida. Introduce un número entero.")

    def sumar_cantidad(self):
        if self.df is None or self.indice_actual is None:
            messagebox.showerror("Error", "Selecciona un producto de la lista primero.")
            return
        cantidad_adicional = self.entrada_cantidad.get()
        try:
            cantidad_adicional = int(cantidad_adicional)
            actual = int(self.df.at[self.indice_actual, self.df.columns[3]])
            self.df.at[self.indice_actual, self.df.columns[3]] = actual + cantidad_adicional
            self.guardar_csv()
            messagebox.showinfo("Cantidad sumada", f"Se sumaron {cantidad_adicional} unidades.")
            self.entrada_cantidad.delete(0, tk.END)
            self.mostrar_detalles()
            fila = self.df.loc[self.indice_actual]
            self.actualizar_ultimo_producto(fila)
            self.entrada_busqueda.focus_set()
            self.entrada_busqueda.select_range(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Introduce una cantidad válida para sumar.")

    def actualizar_ultimo_producto(self, fila):
        try:
            self.texto_ultimo.set(
                f"Modificado: {fila[0]} - {fila[1]} | Cantidad: {fila[3]}"
            )
        except:
            self.texto_ultimo.set("Último producto modificado: (Error de datos)")

    def abrir_formulario_producto(self):
        if self.df is None:
            messagebox.showerror("Error", "Primero carga un archivo CSV.")
            return

        form = tk.Toplevel(self.root)
        form.title("Agregar nuevo producto")
        form.configure(bg="#d9ecff")

        labels = list(self.df.columns)
        entries = []

        for i, texto in enumerate(labels):
            tk.Label(form, text=texto, font=self.fuente, bg="#d9ecff").grid(row=i, column=0, padx=5, pady=5)
            entrada = tk.Entry(form, font=self.fuente, bg="#ffffff")
            entrada.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entrada)

        def guardar():
            try:
                nuevo = [e.get() for e in entries]
                nuevo_dict = dict(zip(self.df.columns, nuevo))
                nuevo_dict[self.df.columns[3]] = int(nuevo_dict[self.df.columns[3]])
                nuevo_dict[self.df.columns[4]] = int(nuevo_dict[self.df.columns[4]])
                self.df.loc[len(self.df)] = nuevo_dict
                self.guardar_csv()
                messagebox.showinfo("Éxito", "Producto agregado correctamente.")
                form.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Verifica los datos: {e}")

        tk.Button(form, text="Guardar", font=self.fuente, bg="#0073e6", fg="white",
                  relief="raised", bd=3, command=guardar).grid(row=len(labels), column=0, columnspan=2, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventarioApp(root)
    root.mainloop()
