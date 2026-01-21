from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import socket # Para diagnosticar la red

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=base_dir)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuración
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587 # Volvemos al 587 pero con un ajuste de conexión
SENDER_EMAIL = 'artesaniasmaderex@gmail.com'
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
VENDOR_EMAIL = 'artesaniasmaderex@gmail.com'

@app.route('/')
def serve_index():
    return send_from_directory(base_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(base_dir, path)

@app.route('/api/send-order', methods=['POST'])
def send_order():
    data = request.json
    try:
        # PRUEBA DE RED ANTES DE ENVIAR
        socket.create_connection(("smtp.gmail.com", 587), timeout=5)
        
        send_email_to_client(data)
        send_email_to_vendor(data)
        return jsonify({'success': True}), 200
    except Exception as e:
        print(f"DEBUG: Fallo de red detectado: {e}")
        return jsonify({'error': f"Error de red: {str(e)}"}), 500

def _send_smtp_email(to_email, msg):
    # Usamos la conexión estándar con timeout explícito
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15)
    server.ehlo()
    server.starttls()
    server.login(SENDER_EMAIL, SMTP_PASSWORD)
    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    server.quit()

def send_email_to_client(order_data):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = order_data['correoCliente']
    msg['Subject'] = "Confirmación Pedido"
    msg.attach(MIMEText(f"Pedido recibido: {order_data['producto_nombre']}", 'plain'))
    _send_smtp_email(order_data['correoCliente'], msg)

def send_email_to_vendor(order_data):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = VENDOR_EMAIL
    msg['Subject'] = "NUEVO PEDIDO"
    msg.attach(MIMEText(f"Producto: {order_data['producto_nombre']}\nCliente: {order_data['nombre']}", 'plain'))
    _send_smtp_email(VENDOR_EMAIL, msg)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
