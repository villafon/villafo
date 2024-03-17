from flask import Flask, redirect, request, render_template, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import os
import signal
from random import randint

app = Flask(__name__)

# Verifica si la carpeta "static" existe, si no, la crea
static_folder = os.path.join(app.root_path, 'static')
if not os.path.exists(static_folder):
    os.makedirs(static_folder)

# Ruta donde se encuentran las facturas
app.config['static_folder'] = static_folder

# Función para obtener las 10 facturas más recientes
def obtener_ultimas_facturas():
    facturas = os.listdir(static_folder)
    facturas.sort(reverse=True)  # Ordenar de manera descendente por fecha de modificación
    return facturas[:10]

# Ruta principal
@app.route('/buscarf', methods=['GET', 'POST'])
def buscarf():
    if request.method == 'POST':
        numero_factura = request.form['numero_factura']
        filename = f"Factura_Villafon{numero_factura}.pdf"
        filepath = os.path.join(app.config['static_folder'], filename)
        if os.path.exists(filepath):
            return redirect(url_for('ver_factura', filename=filename))
        else:
            return "Factura no encontrada"
    else:
        ultimas_facturas = obtener_ultimas_facturas()
        return render_template('buscarf.html', ultimas_facturas=ultimas_facturas)

# Ruta para ver una factura específica
@app.route('/ver_factura/<filename>')
def ver_factura(filename):
    filepath = os.path.join(app.config['static_folder'], filename)
    return redirect(url_for('static', filename=os.path.basename(filepath)))

class Factura:
    def __init__(self, cliente, elementos):
        self.cliente = cliente
        self.elementos = elementos
        self.numero_factura = ''.join(["{}".format(randint(0, 9)) for num in range(0, 12)])

    def generar_factura(self, envio):
        total = 0
        subtotal = 0
        filename = os.path.join(static_folder, "Factura_Villafon{}.pdf".format(self.numero_factura))
        c = canvas.Canvas(filename, pagesize=letter)
        image_path = os.path.join(os.path.dirname(__file__), 'img/icono.png')
        c.drawImage(image_path, 250, 500, 420, 190, preserveAspectRatio=True)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(220, 600, "Villafon")
        c.setFont("Helvetica", 12)
        c.drawString(100, 500, "Factura N°: {}".format(self.numero_factura))
        c.drawString(100, 480, "Fecha: {}".format(datetime.now().strftime("%d/%m/%Y")))
        c.drawString(100, 460, "Cliente: {}".format(self.cliente))
        c.line(100, 450, 500, 450)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, 435, "Descripción")
        c.drawString(400, 435, "Precio (L)")
        c.setFont("Helvetica", 12)
        c.line(100, 430, 500, 430)
        y = 410
        for elemento, precio in self.elementos.items():
            c.drawString(100, y, elemento)
            c.drawString(400, y, "L {:,.2f}".format(precio))
            y -= 30
            subtotal += precio
            total += precio
        c.line(100, y, 500, y)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y - 30, "Subtotal:")
        c.setFont("Helvetica", 12)
        c.drawString(400, y - 30, "L {:,.2f}".format(subtotal))
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y - 60, "Envío:")
        c.setFont("Helvetica", 12)
        c.drawString(400, y - 60, "L {:,.2f}".format(envio))
        total += envio
        c.setFont("Helvetica-Bold", 12)
        c.drawString(100, y - 90, "Total:")
        c.setFont("Helvetica", 12)
        c.drawString(400, y - 90, "L {:,.2f}".format(total))
        image_path_barra = os.path.join(os.path.dirname(__file__), 'img/barra.png')
        c.drawImage(image_path_barra, 0, -15, width=612, height=50, preserveAspectRatio=False)
        c.save()
        return filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar')
def generar():
    return render_template('generar.html')

@app.route('/factura', methods=['POST'])
def generar_factura():
    cliente = request.form['cliente']
    elementos = {}
    num_elementos = int(request.form['num_elementos'])
    for i in range(num_elementos):
        descripcion = request.form[f'descripcion_{i}']
        precio = float(request.form[f'precio_{i}'])
        elementos[descripcion] = precio
    envio = float(request.form['envio'])
    factura = Factura(cliente, elementos)
    filename = factura.generar_factura(envio)
    return redirect(url_for('static', filename=os.path.basename(filename)))

@app.route('/cerrar', methods=['POST'])
def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return 'Programa apagado'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
