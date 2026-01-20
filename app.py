from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --- CONFIGURACIÓN DE RUTAS ---
# Esto asegura que Flask encuentre los archivos en Render
base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=base_dir)
CORS(app)

# --- CONFIGURACIÓN DE CORREO ---
SMTP_SERVER = 'smtp.gmail.com' 
SMTP_PORT = 587
SENDER_EMAIL = 'artesaniasmaderex@gmail.com'
# Se lee la clave desde las variables de entorno de Render
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') 
VENDOR_EMAIL = 'artesaniasmaderex@gmail.com'

# --- RUTAS DE NAVEGACIÓN (Para que se vea la web) ---

@app.route('/')
def serve_index():
    """Sirve el archivo index.html principal"""
    return send_from_directory(base_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Sirve CSS, JS e imágenes"""
    return send_from_directory(base_dir, path)

# --- RUTA DE LÓGICA (Envío de pedidos) ---

@app.route('/api/send-order', methods=['POST'])
def send_order():
    data = request.json

    # Validación básica de datos
    required = ['ubicacion', 'nombre', 'telefono', 'correoCliente', 'producto_nombre']
    if not all(k in data for k in required):
        return jsonify({'error': 'Faltan datos requeridos en el formulario.'}), 400

    try:
        # Enviar correos
        send_email_to_client(data)
        send_email_to_vendor(data)
        return jsonify({'success': True, 'message': 'Pedido enviado correctamente.'}), 200

    except smtplib.SMTPAuthenticationError:
        return jsonify({'error': 'Error de Gmail: Revisa la SMTP_PASSWORD en Render.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- FUNCIONES DE CORREO ---

def _build_email_message(subject, to_email, html_body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
    return msg

def _send_smtp_email(to_email, msg):
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls() 
    server.login(SENDER_EMAIL, SMTP_PASSWORD)
    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    server.quit()

def send_email_to_client(order_data):
    subject = f"✅ Confirmación de Pedido: {order_data['producto_nombre']}"
    html_body = f"""
    <html>
        <body>
            <h2>¡Hola {order_data['nombre']}!</h2>
            <p>Tu pedido de <b>{order_data['producto_nombre']}</b> ha sido recibido.</p>
            <p>Precio: {order_data['producto_precio']}</p>
            <p>Nos contactaremos al {order_data['telefono']} para coordinar en {order_data['ubicacion']}.</p>
        </body>
    </html>
    """
    msg = _build_email_message(subject, order_data['correoCliente'], html_body)
    _send_smtp_email(order_data['correoCliente'], msg)

def send_email_to_vendor(order_data):
    subject = f"🚨 NUEVO PEDIDO: {order_data['producto_nombre']}"
    html_body = f"""
    <html>
        <body>
            <h2>Detalles del Pedido</h2>
            <p><b>Producto:</b> {order_data['producto_nombre']}</p>
            <p><b>Cliente:</b> {order_data['nombre']}</p>
            <p><b>Teléfono:</b> {order_data['telefono']}</p>
            <p><b>Ubicación:</b> {order_data['ubicacion']}</p>
        </body>
    </html>
    """
    msg = _build_email_message(subject, VENDOR_EMAIL, html_body)
    _send_smtp_email(VENDOR_EMAIL, msg)

if __name__ == '__main__':
    # Render usa la variable PORT automáticamente
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
