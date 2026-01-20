from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --- CONFIGURACIÓN DE CORREO Y SERVIDOR ---
# 🚨 REVISA ESTOS VALORES antes de ejecutar 🚨

SMTP_SERVER = 'smtp.gmail.com' 
SMTP_PORT = 587
SENDER_EMAIL = 'artesaniasmaderex@gmail.com' # 🚨 TU CORREO (el que usa el código para enviar)
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') # 🚨 TU CLAVE DE APLICACIÓN/CONTRASEÑA SMTP
VENDOR_EMAIL = 'artesaniasmaderex@gmail.com' # 🚨 TU CORREO (donde recibirás el pedido)

app = Flask(__name__)
CORS(app) 
# ------------------------------------------

@app.route('/api/send-order', methods=['POST'])
def send_order():
    """Maneja la solicitud POST, procesa los datos y envía los dos correos."""
    data = request.json

    if not all(k in data for k in ['ubicacion', 'nombre', 'telefono', 'correoCliente', 'producto_nombre']):
        return jsonify({'error': 'Faltan datos requeridos del formulario.'}), 400

    try:
        # Intenta enviar los correos
        send_email_to_client(data)
        send_email_to_vendor(data)
        
        return jsonify({'success': True, 'message': 'Pedidos enviados correctamente.'}), 200

    except smtplib.SMTPAuthenticationError:
        # Captura errores de inicio de sesión de SMTP (clave incorrecta)
        error_msg = 'ERROR DE AUTENTICACIÓN: El usuario o contraseña de correo son incorrectos (SMTP). Verifica tu SENDER_EMAIL y SMTP_PASSWORD.'
        print(f"Error de Correo: {error_msg}")
        # Devuelve un código de error 500 para que el frontend lo muestre
        return jsonify({'error': error_msg}), 500
        
    except Exception as e:
        # Captura cualquier otro error de conexión o servidor
        error_msg = f'Error interno del servidor: {e}. Revisa si el puerto 587 está bloqueado por el Firewall.'
        print(f"Error Genérico: {e}")
        return jsonify({'error': error_msg}), 500


def _build_email_message(subject, to_email, html_body):
    """Función auxiliar para construir el objeto del mensaje de correo."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_body, 'html'))
    return msg


def _send_smtp_email(to_email, msg):
    """Función auxiliar para conectarse al servidor SMTP y enviar el correo."""
    # Nota: si esta función falla (por credenciales o conexión), el error es capturado
    # en la función 'send_order' de arriba.
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls() 
    server.login(SENDER_EMAIL, SMTP_PASSWORD)
    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    server.quit()


def send_email_to_client(order_data):
    """Envía el mensaje de confirmación y agradecimiento al cliente."""
    subject = f"✅ Confirmación de Pedido: {order_data['producto_nombre']}"
    html_body = f"""
    <html>
        <body>
            <h2>¡Hola {order_data['nombre']}! Tu pedido ha sido confirmado.</h2>
            <p>Muchas gracias por tu compra. Hemos reservado el siguiente producto:</p>
            <ul>
                <li><strong>Artículo:</strong> {order_data['producto_nombre']}</li>
                <li><strong>Precio:</strong> {order_data['producto_precio']}</li>
            </ul>
            <p>En breve nos comunicaremos contigo al número **{order_data['telefono']}** para coordinar la entrega en **{order_data['ubicacion']}**.</p>
            <p>¡Esperamos que disfrutes tu compra!</p>
        </body>
    </html>
    """
    msg = _build_email_message(subject, order_data['correoCliente'], html_body)
    _send_smtp_email(order_data['correoCliente'], msg)


def send_email_to_vendor(order_data):
    """Envía todos los datos del pedido al vendedor."""
    subject = f"🚨 NUEVO PEDIDO RECIBIDO: {order_data['producto_nombre']}"
    html_body = f"""
    <html>
        <body>
            <h2>Detalles del Nuevo Pedido</h2>
            <hr>
            <h3>Producto Solicitado:</h3>
            <ul>
                <li><strong>Nombre:</strong> {order_data['producto_nombre']}</li>
                <li><strong>Precio:</strong> {order_data['producto_precio']}</li>
                <li><strong>Imagen (URL):</strong> <a href="{order_data['producto_imagen']}">Ver Imagen</a></li>
                <img src="{order_data['producto_imagen']}" alt="Producto" style="width:150px; height:auto; margin-top:10px;">
            </ul>
            
            <h3>Datos del Comprador:</h3>
            <ul>
                <li><strong>Nombre:</strong> {order_data['nombre']}</li>
                <li><strong>Ubicación/Dirección:</strong> {order_data['ubicacion']}</li>
                <li><strong>Teléfono:</strong> {order_data['telefono']}</li>
                <li><strong>Correo Cliente:</strong> {order_data['correoCliente']}</li>
            </ul>
        </body>
    </html>
    """
    msg = _build_email_message(subject, VENDOR_EMAIL, html_body)
    _send_smtp_email(VENDOR_EMAIL, msg)


if __name__ == '__main__':
    # Inicia el servidor en el puerto 5000
    app.run(debug=True, port=5000)
