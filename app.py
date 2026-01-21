from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --- CONFIGURACIÓN DE RUTAS ---
base_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_folder=base_dir)
# Configuración de CORS para permitir peticiones desde cualquier origen
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- CONFIGURACIÓN DE CORREO (USANDO SSL PUERTO 465) ---
SMTP_SERVER = 'smtp.gmail.com' 
SMTP_PORT = 465  # Puerto SSL directo
SENDER_EMAIL = 'artesaniasmaderex@gmail.com'
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') 
VENDOR_EMAIL = 'elifalero2013@gmail.com'

# --- RUTAS PARA MOSTRAR LA WEB ---

@app.route('/')
def serve_index():
    return send_from_directory(base_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(base_dir, path)

# --- LÓGICA DE ENVÍO ---

@app.route('/api/send-order', methods=['POST'])
def send_order():
    data = request.json
    
    # Validar que lleguen los datos necesarios
    required = ['ubicacion', 'nombre', 'telefono', 'correoCliente', 'producto_nombre']
    if not data or not all(k in data for k in required):
        return jsonify({'error': 'Faltan datos obligatorios'}), 400

    try:
        # Intentamos enviar los correos
        send_email_to_client(data)
        send_email_to_vendor(data)
        return jsonify({'success': True, 'message': 'Pedido enviado con éxito'}), 200

    except Exception as e:
        print(f"Error en el servidor: {str(e)}")
        return jsonify({'error': str(e)}), 500

# --- FUNCIONES DE CORREO ---

def _send_smtp_email(to_email, msg):
    """Conexión optimizada con SSL para evitar Timeouts"""
    # Usamos SMTP_SSL para una conexión inmediata y segura
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.login(SENDER_EMAIL, SMTP_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

def send_email_to_client(order_data):
    subject = f"✅ Confirmación de Pedido: {order_data['producto_nombre']}"
    html_body = f"""
    <html>
        <body>
            <h2>¡Hola {order_data['nombre']}!</h2>
            <p>Hemos recibido tu pedido de: <b>{order_data['producto_nombre']}</b></p>
            <p>Precio: {order_data['producto_precio']}</p>
            <p>Nos comunicaremos al {order_data['telefono']} para la entrega.</p>
        </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = order_data['correoCliente']
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
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
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = VENDOR_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
    _send_smtp_email(VENDOR_EMAIL, msg)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
