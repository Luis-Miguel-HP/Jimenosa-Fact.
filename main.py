import os
import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import random
import json

# Cargar productos desde un archivo JSON
with open("productos.json", "r") as file:
    productos = json.load(file)

# Crear la carpeta "Cotizaciones" si no existe
carpeta_cotizaciones = "Cotizaciones"
if not os.path.exists(carpeta_cotizaciones):
    os.makedirs(carpeta_cotizaciones)

# Crear la carpeta "Facturas" si no existe
carpeta_facturas = "Facturas"
if not os.path.exists(carpeta_facturas):
    os.makedirs(carpeta_facturas)

factura_counter = 1000

def consultar_producto():
    ventana_consulta = tk.Toplevel(ventana_principal)
    ventana_consulta.title("Consultar Producto por ID")
    ventana_consulta.config(bg="#EFEFEF")
    ventana_consulta.geometry("600x400")

    ventana_consulta.grid_columnconfigure(0, weight=1)
    ventana_consulta.grid_columnconfigure(1, weight=1)
    ventana_consulta.grid_rowconfigure(1, weight=1)

    etiqueta_id = crear_etiqueta(ventana_consulta, "ID del Producto:", 0, 0)
    entrada_id = crear_entrada(ventana_consulta, 0, 1)

    texto_informacion = tk.Text(ventana_consulta,
                                height=10,
                                width=50,
                                bg="#F0F0F0",
                                font=("Helvetica", 12))
    texto_informacion.grid(row=1,
                           column=0,
                           columnspan=2,
                           padx=10,
                           pady=5,
                           sticky="nsew")

    def buscar_producto():
        texto_informacion.delete(1.0, tk.END)
        try:
            codigo_producto = int(entrada_id.get())
            producto = next(
                (prod for prod in productos if prod['id'] == codigo_producto),
                None)
            if not producto:
                texto_informacion.insert(tk.END,
                                         "Código de producto no encontrado.")
            else:
                texto_informacion.insert(tk.END, f"ID: {producto['id']}\n")
                texto_informacion.insert(tk.END,
                                         f"Nombre: {producto['nombre']}\n")
                texto_informacion.insert(
                    tk.END, f"Precio: ${producto['precio']:.2f}\n")
        except ValueError:
            texto_informacion.insert(tk.END, "Código de producto inválido.")

    crear_boton(ventana_consulta, "Buscar", buscar_producto, 2, 0, 2)

    def cerrar_ventana_consulta():
        ventana_consulta.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_consulta, "Cerrar", cerrar_ventana_consulta, 3, 0, 2)


def generar_numero_cotizacion():
    return random.randint(1000, 9999)


def generar_numero_factura():
    global factura_counter
    if factura_counter > 20000:
        messagebox.showerror("Error",
                             "Se ha alcanzado el límite máximo de facturas.")
        return None
    factura_num = factura_counter
    factura_counter += 1
    return factura_num


def generar_pdf(tipo_documento, nombre_cliente, rnc_cliente, fecha_documento,
                productos_seleccionados, mano_de_obra, itbis):
    if not all([
            nombre_cliente, rnc_cliente, fecha_documento,
            productos_seleccionados, itbis
    ]):
        messagebox.showerror(
            "Error", "Por favor, complete todos los campos requeridos.")
        return

    if not productos_seleccionados:
        messagebox.showerror("Error", "Debe agregar al menos un producto.")
        return

    if tipo_documento == "Cotización":
        numero_documento = generar_numero_cotizacion()
        carpeta = carpeta_cotizaciones
    elif tipo_documento == "Factura":
        numero_documento = generar_numero_factura()
        if numero_documento is None:
            return
        carpeta = carpeta_facturas
    else:
        messagebox.showerror("Error", "Tipo de documento desconocido.")
        return

    nombre_archivo_pdf = f"{tipo_documento}_{numero_documento}.pdf"
    ruta_pdf = os.path.join(carpeta, nombre_archivo_pdf)
    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    encabezado_style = ParagraphStyle('Heading1',
                                      parent=styles['Heading1'],
                                      fontName='Helvetica-Bold',
                                      fontSize=20,
                                      textColor=colors.black,
                                      spaceAfter=20)
    info_style = ParagraphStyle('Normal',
                                parent=styles['Normal'],
                                fontSize=10,
                                spaceAfter=10,
                                alignment=0)
    total_style = ParagraphStyle('Total',
                                 parent=styles['Normal'],
                                 fontSize=12,
                                 spaceBefore=20,
                                 spaceAfter=10,
                                 textColor=colors.red,
                                 alignment=0)
    table_header_style = ParagraphStyle('TableHeader',
                                        parent=styles['Normal'],
                                        fontSize=8,
                                        textColor=colors.white,
                                        alignment=1,
                                        spaceAfter=12)
    table_data_style = ParagraphStyle('TableData',
                                      parent=styles['Normal'],
                                      fontSize=8,
                                      alignment=1,
                                      spaceAfter=6)
    green_style = ParagraphStyle('GreenStyle',
                                 parent=styles['Normal'],
                                 textColor=colors.HexColor('#4CAF50'),
                                 alignment=0)
    bold_style = ParagraphStyle('BoldStyle',
                                parent=styles['Normal'],
                                fontName='Helvetica-Bold',
                                alignment=0)

    company_info = [
        "Jimosa Group S.R.L", "AVE. WINSTON CHURCHILL NO. 71, EDIF. TUREY",
        "Distrito Nacional, República Dominicana", "Tel. 809-540-8912"
    ]
    client_info = [
        f"<b>Cliente:</b> {nombre_cliente}", f"<b>RNC:</b> {rnc_cliente}",
        f"<b>Fecha:</b> {fecha_documento}",
        f"<b>Número de {tipo_documento}:</b> <font color='black'>{numero_documento}</font>"
    ]

    for line in company_info:
        elements.append(Paragraph(line, green_style))
    elements.append(Spacer(1, 12))

    for line in client_info:
        elements.append(Paragraph(line, info_style))
    elements.append(Spacer(1, 12))

    data = [["ID", "Nombre", "Precio Unitario", "Cantidad", "Precio Total"]]
    total = 0
    for producto in productos_seleccionados:
        data.append([
            producto["id"], producto["nombre"], f"${producto['precio']:.2f}",
            producto["cantidad"],
            f"${producto['precio'] * producto['cantidad']:.2f}"
        ])
        total += producto['precio'] * producto['cantidad']

    table = Table(data)
    table.setStyle(
        TableStyle([('BACKGROUND', (0, 0), (-1, 0),
                     colors.HexColor('#4CAF50')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    mano_de_obra = float(mano_de_obra)
    itbis = float(itbis) / 100 * total

    total_general = total + mano_de_obra + itbis

    total_info = [
        f"<b>Subtotal:</b> ${total:.2f}",
        f"<b>Mano de Obra:</b> ${mano_de_obra:.2f}",
        f"<b>ITBIS (%):</b> ${itbis:.2f}",
        f"<b>Total General:</b> ${total_general:.2f}"
    ]
    for line in total_info:
        elements.append(Paragraph(line, total_style))

    doc.build(elements)

    messagebox.showinfo(
        "Éxito", f"{tipo_documento} guardada como {nombre_archivo_pdf}")


def crear_cotizacion():
    crear_documento("Cotización")


def crear_factura():
    crear_documento("Factura")


def crear_documento(tipo_documento):
    ventana_documento = tk.Toplevel(ventana_principal)
    ventana_documento.title(f"Crear {tipo_documento}")
    ventana_documento.config(bg="#EFEFEF")
    ventana_documento.geometry("800x600")

    for i in range(12):
        ventana_documento.grid_rowconfigure(i, weight=1)
    for i in range(2):
        ventana_documento.grid_columnconfigure(i, weight=1)

    etiqueta_nombre_cliente = crear_etiqueta(ventana_documento,
                                             "Nombre del Cliente:", 0, 0)
    entrada_nombre_cliente = crear_entrada(ventana_documento, 0, 1)

    etiqueta_rnc_cliente = crear_etiqueta(ventana_documento, "RNC del Cliente:",
                                          1, 0)
    entrada_rnc_cliente = crear_entrada(ventana_documento, 1, 1)

    etiqueta_fecha_documento = crear_etiqueta(ventana_documento, "Fecha:", 2, 0)
    entrada_fecha_documento = crear_entrada(ventana_documento, 2, 1)

    frame_productos = ttk.Frame(ventana_documento, padding="10")
    frame_productos.grid(row=3, column=0, columnspan=2, sticky="nsew")

    productos_seleccionados = []

    etiqueta_id_producto = crear_etiqueta(frame_productos, "ID del Producto:",
                                          0, 0)
    entrada_id_producto = crear_entrada(frame_productos, 0, 1)

    etiqueta_cantidad_producto = crear_etiqueta(frame_productos, "Cantidad:",
                                                1, 0)
    entrada_cantidad_producto = crear_entrada(frame_productos, 1, 1)

    frame_lista_productos = ttk.Frame(ventana_documento, padding="10")
    frame_lista_productos.grid(row=4, column=0, columnspan=2, sticky="nsew")

    ventana_documento.grid_rowconfigure(4, weight=3)
    frame_lista_productos.grid_rowconfigure(0, weight=1)
    frame_lista_productos.grid_columnconfigure(0, weight=1)

    scrollbar = tk.Scrollbar(frame_lista_productos)
    scrollbar.grid(row=0, column=1, sticky="ns")

    lista_productos = tk.Listbox(frame_lista_productos,
                                 yscrollcommand=scrollbar.set,
                                 font=("Helvetica", 10))
    lista_productos.grid(row=0, column=0, sticky="nsew")
    scrollbar.config(command=lista_productos.yview)

    def agregar_producto():
        try:
            codigo_producto = int(entrada_id_producto.get())
            cantidad_producto = int(entrada_cantidad_producto.get())
            producto = next(
                (prod for prod in productos if prod['id'] == codigo_producto),
                None)
            if not producto:
                messagebox.showerror("Error", "Código de producto no encontrado.")
                return

            producto_seleccionado = {
                "id": producto["id"],
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": cantidad_producto
            }

            productos_seleccionados.append(producto_seleccionado)

            lista_productos.insert(tk.END, f"ID: {producto_seleccionado['id']}, "
                                           f"Nombre: {producto_seleccionado['nombre']}, "
                                           f"Precio: ${producto_seleccionado['precio']:.2f}, "
                                           f"Cantidad: {producto_seleccionado['cantidad']}")
            entrada_id_producto.delete(0, tk.END)
            entrada_cantidad_producto.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Código o cantidad inválidos.")

    def eliminar_producto():
        seleccion = lista_productos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar.")
            return

        indice = seleccion[0]
        lista_productos.delete(indice)
        productos_seleccionados.pop(indice)

    crear_boton(frame_productos, "Agregar Producto", agregar_producto, 2, 0)
    crear_boton(frame_productos, "Eliminar Producto", eliminar_producto, 2, 1)

    etiqueta_mano_de_obra = crear_etiqueta(ventana_documento, "Mano de Obra:", 5, 0)
    entrada_mano_de_obra = crear_entrada(ventana_documento, 5, 1)

    etiqueta_itbis = crear_etiqueta(ventana_documento, "ITBIS (%):", 6, 0)
    entrada_itbis = crear_entrada(ventana_documento, 6, 1)

    def generar_documento_pdf():
        nombre_cliente = entrada_nombre_cliente.get()
        rnc_cliente = entrada_rnc_cliente.get()
        fecha_documento = entrada_fecha_documento.get()
        mano_de_obra = entrada_mano_de_obra.get()
        itbis = entrada_itbis.get()
        generar_pdf(tipo_documento, nombre_cliente, rnc_cliente, fecha_documento,
                    productos_seleccionados, mano_de_obra, itbis)

    crear_boton(ventana_documento, f"Generar {tipo_documento}", generar_documento_pdf, 7, 0, 2)

    def cerrar_ventana_documento():
        ventana_documento.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_documento, "Cerrar", cerrar_ventana_documento, 8, 0, 2)


def crear_etiqueta(ventana, texto, fila, columna):
    etiqueta = tk.Label(ventana,
                        text=texto,
                        font=("Helvetica", 12, "bold"),
                        bg="#4CAF50",
                        fg="white",
                        padx=10,
                        pady=5)
    etiqueta.grid(row=fila, column=columna, sticky="w", padx=10, pady=5)
    return etiqueta


def crear_entrada(ventana, fila, columna):
    entrada = ttk.Entry(ventana, font=("Helvetica", 12))
    entrada.grid(row=fila, column=columna, padx=10, pady=5, sticky="ew")
    return entrada


def crear_boton(ventana, texto, comando, fila, columna, colspan=1, estilo="Custom.TButton"):
    boton = ttk.Button(ventana,
                       text=texto,
                       command=comando,
                       style=estilo)
    boton.grid(row=fila,
               column=columna,
               columnspan=colspan,
               padx=10,
               pady=5,
               sticky="ew")
    return boton


ventana_principal = tk.Tk()
ventana_principal.title("Sistema de Cotizaciones y Facturación")
ventana_principal.config(bg="#EFEFEF")
ventana_principal.geometry("600x400")

for i in range(5):
    ventana_principal.grid_rowconfigure(i, weight=1)
ventana_principal.grid_columnconfigure(0, weight=1)

style = ttk.Style()
style.configure("Custom.TButton",
                font=("Helvetica", 12, "bold"),
                background="#2196F3",
                foreground="white",
                padding=10)
style.map("Custom.TButton", background=[("active", "#1976D2")])

style.configure("Green.TButton",
                font=("Helvetica", 12, "bold"),
                background="#4CAF50",
                foreground="white",
                padding=10)
style.map("Green.TButton", background=[("active", "#388E3C")])

# Añadir el título de bienvenida con estilo verde
crear_boton(ventana_principal, "¡Bienvenido a Jimenosa Group S.R.L!", None, 0, 0, estilo="Green.TButton")

# Ajustar las posiciones de los botones
crear_boton(ventana_principal, "Consultar Producto", consultar_producto, 1, 0)
crear_boton(ventana_principal, "Crear Cotización", crear_cotizacion, 2, 0)
crear_boton(ventana_principal, "Crear Factura", crear_factura, 3, 0)
crear_boton(ventana_principal, "Salir", ventana_principal.quit, 4, 0)

ventana_principal.mainloop()
