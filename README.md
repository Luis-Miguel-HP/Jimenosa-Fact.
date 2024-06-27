Sistema de Gestión de Cotizaciones y Facturas
Este sistema permite gestionar cotizaciones y facturas para clientes, incluyendo la consulta y modificación de productos, así como la generación de documentos PDF.

             Características
Consulta de productos: Busca productos por su ID.
Generación de cotizaciones y facturas: Crea documentos PDF detallados con la información de los clientes y productos seleccionados.
Consulta de cotizaciones: Muestra una lista de cotizaciones existentes y permite cambiar su estado o eliminarlas.
Cambio de precios de productos: Modifica los precios de los productos existentes.


Requisitos
Python 3.x
Bibliotecas necesarias (pueden instalarse mediante pip):
pip install reportlab


         Estructura del proyecto
main.py: Código fuente principal del programa.
productos.json: Archivo JSON con la información de los productos.
clientes.json: Archivo JSON con la información de los clientes.
cotizaciones.json: Archivo JSON donde se almacenan las cotizaciones generadas.
Cotizaciones/: Carpeta donde se almacenan las cotizaciones en formato PDF.
Facturas/: Carpeta donde se almacenan las facturas en formato PDF.


Ejecutar el programa:



python main.py


Consultar productos:
Seleccione la opción "Consultar Producto" en la ventana principal.
Ingrese el ID del producto y haga clic en "Buscar".
Generar una cotización:

Seleccione la opción "Crear Cotización" en la ventana principal.
Complete la información requerida y agregue los productos.
Haga clic en "Generar Cotización" para crear el documento PDF.
Generar una factura:

Seleccione la opción "Crear Factura" en la ventana principal.
Complete la información requerida y agregue los productos.
Haga clic en "Generar Factura" para crear el documento PDF.
Consultar cotizaciones:

Seleccione la opción "Consultar Cotizaciones" en la ventana principal.
Visualice, cambie el estado o elimine las cotizaciones.
Cambiar precios de productos:

Seleccione la opción "Cambiar Producto" en la ventana principal.
Seleccione un producto y modifique su precio.
Notas
Asegúrese de que los archivos productos.json y clientes.json estén en el mismo directorio que main.py.
Las cotizaciones y facturas generadas se almacenan en las carpetas Cotizaciones y Facturas, respectivamente.
Contribución
Si desea contribuir a este proyecto, puede clonar el repositorio y enviar sus mejoras a través de pull requests.
