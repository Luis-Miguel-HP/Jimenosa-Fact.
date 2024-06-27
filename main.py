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

# Cargar clientes desde un archivo JSON
with open("clientes.json", "r") as file:
    clientes = json.load(file)

# Crear la carpeta "Cotizaciones" si no existe
carpeta_cotizaciones = "Cotizaciones"
if not os.path.exists(carpeta_cotizaciones):
    os.makedirs(carpeta_cotizaciones)

# Crear la carpeta "Facturas" si no existe
carpeta_facturas = "Facturas"
if not os.path.exists(carpeta_facturas):
    os.makedirs(carpeta_facturas)

# Carpeta para almacenar las facturas y nombre del archivo JSON
archivo_cotizaciones = "cotizaciones.json"

# Load quotations from the JSON file or initialize an empty list
if os.path.exists(archivo_cotizaciones):
    with open(archivo_cotizaciones, "r") as file:
        cotizaciones = json.load(file)
else:
    cotizaciones = []

# Crear la carpeta "Facturas" si no existe
if not os.path.exists(carpeta_facturas):
    os.makedirs(carpeta_facturas)

factura_counter = 1000  # Contador para generar números de factura


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
    # Obtener el número más alto de factura existente
    ultima_factura_existente = max(
        int(f.split("_")[1].split(".")[0])
        for f in os.listdir(carpeta_facturas)
        if f.startswith("Factura_")) if os.listdir(carpeta_facturas) else 0
    factura_counter = max(factura_counter, ultima_factura_existente + 1)
    return factura_counter



def generar_pdf(tipo_documento, nombre_cliente, rnc_cliente, fecha_documento,
                productos_seleccionados, mano_de_obra, itbis, comentario):
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
                                alignment=2)
    total_style = ParagraphStyle('Total',
                                 parent=styles['Normal'],
                                 fontSize=18,
                                 spaceBefore=18,
                                 spaceAfter=18,
                                 textColor=colors.black,
                                 alignment=2)
    table_header_style = ParagraphStyle('TableHeader',
                                        parent=styles['Normal'],
                                        fontSize=10,
                                        textColor=colors.white,
                                        alignment=1,
                                        spaceAfter=12)
    table_data_style = ParagraphStyle('TableData',
                                      parent=styles['Normal'],
                                      fontSize=10,
                                      alignment=1,
                                      spaceAfter=6)
    green_style = ParagraphStyle('GreenStyle',
                                 parent=styles['Normal'],
                                 textColor=colors.black,
                                 alignment=0)
    bold_style = ParagraphStyle('BoldStyle',
                                parent=styles['Normal'],
                                fontName='Helvetica-Bold',
                                alignment=0)

    company_info = [
        "CALLE ALEXANDER FLEMING #8, ENSACHE LA FE ", "D.N, Rep. Dom.",
        "Tel. 829-584-7810"
    ]
    client_info = [
        f"<b>Cliente:</b> {nombre_cliente}", f"<b>RNC:</b> {rnc_cliente}",
        f"<b>Fecha:</b> {fecha_documento}",
        f"<b>No. {tipo_documento}:</b> <font color='black'>{numero_documento}</font>"
    ]

    for line in company_info:
        elements.append(Paragraph(line, green_style))
    elements.append(Spacer(1, 12))

    for line in client_info:
        elements.append(Paragraph(line, info_style))
    elements.append(Spacer(1, 12))

    # Definir encabezado de tabla basado en si los comentarios están presentes o no
    if any(producto.get('comentario') for producto in productos_seleccionados):
        data = [[
            "Nombre", "Descripción", "Cantidad", "Precio Unitario", "ITBIS (%)", "ITBIS", "Precio Total"
        ]]
    else:
        data = [[
            "Nombre", "Cantidad", "Precio Unitario", "ITBIS (%)", "ITBIS", "Precio Total"
        ]]

    total = 0
    for producto in productos_seleccionados:
        itbis_producto = (producto['precio'] * producto['cantidad'] *
                          producto['itbis'] / 100)
        precio_total_producto = producto['precio'] * producto[
            'cantidad'] + itbis_producto
        # Agregar filas de datos basado en si los comentarios están presentes o no
        if producto.get('comentario'):
            data.append([
                producto["nombre"], f"{producto['comentario']}", producto['cantidad'],
                f"RD${producto['precio']:.2f}", f"{producto['itbis']}%",
                f"RD${itbis_producto:.2f}", f"RD${precio_total_producto:.2f}"
            ])
        else:
            data.append([
                producto["nombre"], producto['cantidad'],
                f"RD${producto['precio']:.2f}", f"{producto['itbis']}%",
                f"RD${itbis_producto:.2f}", f"RD${precio_total_producto:.2f}"
            ])
        total += precio_total_producto

    table = Table(data)
    table.setStyle(
        TableStyle([('BACKGROUND', (0, 0), (-1, 0),
                     colors.HexColor('#03b1fc')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    mano_de_obra = float(mano_de_obra)
    total_general = total + mano_de_obra

    if tipo_documento == "Cotización":
        cotizacion_info = {
            "numero": numero_documento,
            "nombre_cliente": nombre_cliente,
            "monto": total_general,
            "estado": "pendiente"
        }
        cotizaciones.append(cotizacion_info)
        with open(archivo_cotizaciones, "w") as file:
            json.dump(cotizaciones, file, indent=4)

    total_info = [
        f"<b>Subtotal:</b> RD${total:.2f}",
        f"<b>Mano de Obra:</b> RD${mano_de_obra:.2f}",
        f"<b>Total General:</b> RD${total_general:.2f}"
    ]
    for line in total_info:
        elements.append(Paragraph(line, total_style))

    doc.build(elements)

    messagebox.showinfo(
        "Éxito", f"{tipo_documento} guardada como {nombre_archivo_pdf}")



def consultar_cotizacion():
    ventana_consulta = tk.Toplevel(ventana_principal)
    ventana_consulta.title("Consultar Cotizaciones")
    ventana_consulta.config(bg="#EFEFEF")
    ventana_consulta.geometry("800x400")

    ventana_consulta.grid_columnconfigure(0, weight=1)
    ventana_consulta.grid_columnconfigure(1, weight=1)
    ventana_consulta.grid_rowconfigure(1, weight=1)

    # Encabezados de la tabla
    columnas = ("Número", "Cliente", "Monto", "Estado", "Acciones")
    tree = ttk.Treeview(ventana_consulta, columns=columnas, show="headings")

    for col in columnas:
        tree.heading(col, text=col)
        tree.column(col, anchor=tk.CENTER)

    # Insertar datos de cotizaciones en la tabla
    for cotizacion in cotizaciones:
        tree.insert("",
                    tk.END,
                    values=(cotizacion["numero"], cotizacion["nombre_cliente"],
                            f'RD${cotizacion["monto"]:.2f}',
                            cotizacion["estado"]))

    tree.grid(row=0, column=0, columnspan=2, sticky="nsew")

    # Botón para cerrar la ventana de consulta
    def cerrar_ventana_consulta():
        ventana_consulta.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_consulta, "Cerrar", cerrar_ventana_consulta, 1, 0, 2)

    # Función para cambiar el estado de una cotización
    def cambiar_estado():
        selected_item = tree.selection()[0]
        cotizacion_numero = tree.item(selected_item)["values"][0]
        nuevo_estado = "aceptada" if tree.item(
            selected_item)["values"][3] == "pendiente" else "pendiente"

        # Actualizar el estado en la lista y en la interfaz
        for cotizacion in cotizaciones:
            if cotizacion["numero"] == cotizacion_numero:
                cotizacion["estado"] = nuevo_estado
                break

        tree.item(selected_item,
                  values=(cotizacion_numero,
                          tree.item(selected_item)["values"][1],
                          tree.item(selected_item)["values"][2], nuevo_estado))

        # Guardar los cambios en el archivo JSON
        with open(archivo_cotizaciones, "w") as file:
            json.dump(cotizaciones, file, indent=4)

    # Botón para cambiar el estado
    crear_boton(ventana_consulta, "Cambiar Estado", cambiar_estado, 2, 0, 1)

    # Función para eliminar una cotización
    def eliminar_cotizacion():
        selected_item = tree.selection()[0]
        cotizacion_numero = tree.item(selected_item)["values"][0]

        # Eliminar la cotización de la lista y del archivo JSON
        for cotizacion in cotizaciones:
            if cotizacion["numero"] == cotizacion_numero:
                cotizaciones.remove(cotizacion)
                break

        with open(archivo_cotizaciones, "w") as file:
            json.dump(cotizaciones, file, indent=4)

        # Eliminar la cotización de la interfaz
        tree.delete(selected_item)

        # Eliminar el archivo PDF correspondiente
        archivo_pdf = os.path.join(carpeta_cotizaciones,
                                   f'Cotizacion_{cotizacion_numero}.pdf')
        if os.path.exists(archivo_pdf):
            os.remove(archivo_pdf)

    # Botón para eliminar la cotización
    crear_boton(ventana_consulta, "Eliminar", eliminar_cotizacion, 2, 1, 1)


def crear_cotizacion():
    crear_documento("Cotización")


def crear_factura():
    crear_documento("Factura")


def cargar_rnc(combo_cliente, entrada_rnc):
    cliente_seleccionado = combo_cliente.get()
    if cliente_seleccionado:
        rnc_cliente = next((cliente["rnc"] for cliente in clientes
                            if cliente["nombre"] == cliente_seleccionado), "")
        entrada_rnc.delete(0, tk.END)
        entrada_rnc.insert(0, rnc_cliente)


def crear_documento(tipo_documento):
    ventana_documento = tk.Toplevel(ventana_principal)
    ventana_documento.title(f"Crear {tipo_documento}")
    ventana_documento.config(bg="#EFEFEF")
    ventana_documento.geometry("800x600")

    combo_nombre_cliente = ttk.Combobox(ventana_documento,
                                        font=("Helvetica", 12))
    entrada_rnc_cliente = ttk.Entry(ventana_documento, font=("Helvetica", 12))
    entrada_comentario_mano_obra = ttk.Entry(ventana_documento,
                                             font=("Helvetica", 12))

    for i in range(12):
        ventana_documento.grid_rowconfigure(i, weight=1)
    for i in range(2):
        ventana_documento.grid_columnconfigure(i, weight=1)

    etiqueta_nombre_cliente = crear_etiqueta(ventana_documento,
                                             "Nombre del Cliente:", 0, 0)
    combo_nombre_cliente["values"] = [
        cliente["nombre"] for cliente in clientes
    ]
    combo_nombre_cliente.bind(
        "<<ComboboxSelected>>",
        lambda event: cargar_rnc(combo_nombre_cliente, entrada_rnc_cliente))
    combo_nombre_cliente.grid(row=0, column=1)

    etiqueta_rnc_cliente = crear_etiqueta(ventana_documento,
                                          "RNC del Cliente:", 1, 0)
    entrada_rnc_cliente.grid(row=1, column=1)

    etiqueta_fecha_documento = crear_etiqueta(ventana_documento, "Fecha:", 2,
                                              0)
    entrada_fecha_documento = crear_entrada(ventana_documento, 2, 1)

    frame_productos = ttk.Frame(ventana_documento, padding="10")
    frame_productos.grid(row=3, column=0, columnspan=2, sticky="nsew")

    productos_seleccionados = []

    etiqueta_id_producto = crear_etiqueta(frame_productos,
                                          "Nombre del Producto", 0, 0)
    combo_producto = ttk.Combobox(frame_productos, font=("Helvetica", 12))
    combo_producto["values"] = [producto["nombre"] for producto in productos]
    combo_producto.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    etiqueta_cantidad_producto = crear_etiqueta(frame_productos, "Cantidad:",
                                                1, 0)
    entrada_cantidad_producto = crear_entrada(frame_productos, 1, 1)

    etiqueta_itbis_producto = crear_etiqueta(frame_productos,
                                             "ITBIS del Producto (%):", 2, 0)
    entrada_itbis_producto = crear_entrada(frame_productos, 2, 1)

    #etiqueta_comentario_mano_obra = crear_etiqueta(frame_productos, "Comentario:",3,0)
    entrada_comentario_mano_obra = crear_entrada(frame_productos, 3, 1)

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
            etiqueta_id_producto = combo_producto.get()
            cantidad_producto = int(entrada_cantidad_producto.get())
            itbis_producto = float(entrada_itbis_producto.get())
            comentario_producto = entrada_comentario_mano_obra.get()
            producto = next((prod for prod in productos
                             if prod['nombre'] == etiqueta_id_producto), None)
            if not producto:
                messagebox.showerror("Error",
                                     "Código de producto no encontrado.")
                return

            producto_seleccionado = {
                "nombre": producto["nombre"],
                "precio": producto["precio"],
                "cantidad": cantidad_producto,
                "itbis": itbis_producto,
                "comentario": comentario_producto if comentario_producto else None
            }

            productos_seleccionados.append(producto_seleccionado)

            lista_productos.insert(
                tk.END,
                f"nombre: {producto_seleccionado['nombre']}, "
                f"Precio: ${producto_seleccionado['precio']:.2f}, "
                f"Cantidad: {producto_seleccionado['cantidad']}, "
                f"ITBIS: {producto_seleccionado['itbis']}%"
                + (f", Comentario: {producto_seleccionado['comentario']}" if producto_seleccionado['comentario'] else "")
            )

            # Limpiar campos de entrada después de agregar el producto
            combo_producto.set('')  # Limpiar el combobox
            entrada_cantidad_producto.delete(0, tk.END)
            entrada_itbis_producto.delete(0, tk.END)
            entrada_comentario_mano_obra.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error",
                                 "Código, cantidad o ITBIS inválidos.")

    def eliminar_producto():
        seleccion = lista_productos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia",
                                   "Seleccione un producto para eliminar.")
            return

        indice = seleccion[0]
        lista_productos.delete(indice)
        productos_seleccionados.pop(indice)
        entrada_itbis_producto.delete(0, tk.END)

    etiqueta_itbis_producto = crear_etiqueta(frame_productos,
                                             "ITBIS del Producto (%):", 2, 0)
    entrada_itbis_producto = crear_entrada(frame_productos, 2, 1)
    etiqueta_comentario_mano_obra = crear_etiqueta(frame_productos,
                                                   "Comentario:", 3, 0)
    entrada_comentario_mano_obra = crear_entrada(frame_productos, 3, 1)

    crear_boton(frame_productos, "Agregar Producto", agregar_producto, 4, 0)
    crear_boton(frame_productos, "Eliminar Producto", eliminar_producto, 4, 1)

    #etiqueta_itbis = crear_etiqueta(ventana_documento, "ITBIS (%):", 5, 0)
    #entrada_itbis = crear_entrada(ventana_documento, 5, 1)
    etiqueta_mano_de_obra = crear_etiqueta(ventana_documento, "Mano de Obra:",
                                           5, 0)
    entrada_mano_de_obra = crear_entrada(ventana_documento, 5, 1)

    def generar_documento_pdf():
        nombre_cliente = combo_nombre_cliente.get()
        rnc_cliente = entrada_rnc_cliente.get()
        fecha_documento = entrada_fecha_documento.get()
        mano_de_obra = entrada_mano_de_obra.get()
        itbis = entrada_itbis_producto.get()
        comentario = entrada_comentario_mano_obra.get()
        generar_pdf(tipo_documento, nombre_cliente, rnc_cliente,
                    fecha_documento, productos_seleccionados, mano_de_obra,
                    entrada_itbis_producto, comentario)

    crear_boton(ventana_documento, f"Generar {tipo_documento}",
                generar_documento_pdf, 8, 0, 2)

    def cerrar_ventana_documento():
        ventana_documento.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_documento, "Cerrar", cerrar_ventana_documento, 9, 0, 2)


def crear_entrada(ventana, fila, columna):
    entrada = ttk.Entry(ventana, font=("Helvetica", 12))
    entrada.grid(row=fila, column=columna, padx=10, pady=5, sticky="ew")
    return entrada


def crear_boton(ventana,
                texto,
                comando,
                fila,
                columna,
                colspan=1,
                estilo="Custom.TButton"):
    boton = ttk.Button(ventana, text=texto, command=comando, style=estilo)
    boton.grid(row=fila,
               column=columna,
               columnspan=colspan,
               padx=10,
               pady=5,
               sticky="ew")
    return boton


def cambiar_precios(producto, nuevo_precio):
    producto['precio'] = nuevo_precio


# Función para ventana de cambio de precios
def abrir_cambiar_producto():
    ventana_principal.withdraw()

    ventana_cambiar_producto = tk.Toplevel(ventana_principal)
    ventana_cambiar_producto.title("Cambiar Producto")
    ventana_cambiar_producto.config(bg="#EFEFEF")
    ventana_cambiar_producto.geometry("400x200")

    ventana_cambiar_producto.grid_columnconfigure(0, weight=1)
    ventana_cambiar_producto.grid_columnconfigure(1, weight=1)
    ventana_cambiar_producto.grid_rowconfigure(4, weight=1)

    etiqueta_producto = crear_etiqueta(ventana_cambiar_producto, "Producto:",
                                       0, 0)
    combo_productos = ttk.Combobox(ventana_cambiar_producto,
                                   font=("Helvetica", 12))
    combo_productos['values'] = [producto['nombre'] for producto in productos]
    combo_productos.grid(row=0, column=1)

    etiqueta_nuevo_precio = crear_etiqueta(ventana_cambiar_producto,
                                           "Nuevo Precio:", 1, 0)
    entrada_nuevo_precio = crear_entrada(ventana_cambiar_producto, 1, 1)

    def actualizar_precio_producto():
        producto_seleccionado = combo_productos.get()
        nuevo_precio = entrada_nuevo_precio.get()

        if not producto_seleccionado or not nuevo_precio:
            messagebox.showerror(
                "Error",
                "Por favor, seleccione un producto y escriba un nuevo precio.")
            return

        try:
            nuevo_precio = float(nuevo_precio)
        except ValueError:
            messagebox.showerror(
                "Error", "Por favor, ingrese un precio válido (número).")
            return

        for producto in productos:
            if producto['nombre'] == producto_seleccionado:
                producto['precio'] = nuevo_precio
                messagebox.showinfo(
                    "Éxito",
                    f"Precio de '{producto_seleccionado}' actualizado correctamente a {nuevo_precio:.2f}."
                )
                with open("productos.json", "w") as file:
                    json.dump(productos, file, indent=4)
                break
        else:
            messagebox.showerror(
                "Error",
                f"No se encontró el producto '{producto_seleccionado}'.")

    crear_boton(ventana_cambiar_producto, "Actualizar Precio",
                actualizar_precio_producto, 2, 0, 2)

    def cerrar_ventana_cambiar_producto():
        ventana_cambiar_producto.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_cambiar_producto, "Cerrar",
                cerrar_ventana_cambiar_producto, 3, 0, 2)


def abrir_cambiar_precios():
    ventana_principal.withdraw()
    abrir_cambiar_producto()


# Función para crear un nuevo producto
def crear_nuevo_producto(ventana_principal):
    ventana_principal.withdraw()

    ventana_nuevo_producto = tk.Toplevel(ventana_principal)
    ventana_nuevo_producto.title("Crear Nuevo Producto")
    ventana_nuevo_producto.config(bg="#EFEFEF")
    ventana_nuevo_producto.geometry("450x280")
    etiqueta_id_producto = crear_etiqueta(ventana_nuevo_producto,
                                          "ID del Producto:", 0, 0)
    entrada_id_producto = crear_entrada(ventana_nuevo_producto, 0, 1)

    etiqueta_nombre_producto = crear_etiqueta(ventana_nuevo_producto,
                                              "Nombre del Producto:", 1, 0)
    entrada_nombre_producto = crear_entrada(ventana_nuevo_producto, 1, 1)

    etiqueta_precio_producto = crear_etiqueta(ventana_nuevo_producto,
                                              "Precio del Producto:", 2, 0)
    entrada_precio_producto = crear_entrada(ventana_nuevo_producto, 2, 1)

    def guardar_nuevo_producto():
        id_producto = entrada_id_producto.get()
        nombre_producto = entrada_nombre_producto.get()
        precio_producto = entrada_precio_producto.get()

        # Validación de campos
        if not id_producto or not nombre_producto or not precio_producto:
            messagebox.showerror("Error",
                                 "Por favor, complete todos los campos.")
            return

        try:
            id_producto = int(id_producto)
            precio_producto = float(precio_producto)
        except ValueError:
            messagebox.showerror("Error", "ID y precio deben ser números.")
            return

        # Crear diccionario del nuevo producto
        nuevo_producto = {
            "id": id_producto,
            "nombre": nombre_producto,
            "precio": precio_producto
            # Puedes añadir más campos según sea necesario
        }

        # Agregar el nuevo producto a la lista
        productos.append(nuevo_producto)

        # Guardar la lista actualizada en el archivo JSON (simulado)
        with open("productos.json", "w") as file:
            json.dump(productos, file, indent=4)

        messagebox.showinfo("Éxito", "Nuevo producto creado y guardado.")

        ventana_nuevo_producto.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_nuevo_producto, "Guardar", guardar_nuevo_producto, 3,
                0)

    def cerrar_ventana_nuevo_producto():
        ventana_nuevo_producto.destroy()
        ventana_principal.deiconify()

    crear_boton(ventana_nuevo_producto, "Cerrar",
                cerrar_ventana_nuevo_producto, 3, 1)


# Función para abrir la ventana de crear un nuevo producto
def abrir_crear_nuevo_producto():
    ventana_principal.withdraw()
    crear_nuevo_producto(ventana_principal)


# Función para crear etiqueta
def crear_etiqueta(parent, text, row, column):
    etiqueta = tk.Label(parent,
                        text=text,
                        bg="#EFEFEF",
                        font=("Helvetica", 12))
    etiqueta.grid(row=row, column=column, padx=10, pady=5, sticky="w")
    return etiqueta


ventana_principal = tk.Tk()
ventana_principal.title("Sistema de Cotizaciones y Facturación")
ventana_principal.config(bg="#EFEFEF")
ventana_principal.geometry("600x450")

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

crear_boton(ventana_principal,
            "¡Bienvenido a Jimosa Group S.R.L!",
            None,
            0,
            0,
            estilo="Green.TButton")

crear_boton(ventana_principal, "Consultar Producto", consultar_producto, 1, 0)
crear_boton(ventana_principal, "Crear Cotización", crear_cotizacion, 2, 0)
crear_boton(ventana_principal, "Crear Factura", crear_factura, 3, 0)
crear_boton(ventana_principal, "Consultar Cotización", consultar_cotizacion, 4,
            0)
crear_boton(ventana_principal, "Actualizar Precio", abrir_cambiar_precios, 5,
            0)
crear_boton(ventana_principal, "Crear Producto", abrir_crear_nuevo_producto, 6,
            0)
crear_boton(ventana_principal, "Salir", ventana_principal.quit, 7, 0)

ventana_principal.mainloop()
