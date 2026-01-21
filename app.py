from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
import re # Importamos para buscar el ID con facilidad

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=base_dir)
CORS(app)

# Configuración de Resend
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
# CORREO DONDE RECIBES LOS PEDIDOS (Vendedor)
VENDOR_EMAIL = 'artesaniasmaderex@gmail.com' 

@app.route('/')
def serve_index():
    return send_from_directory(base_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(base_dir, path)

def extraer_id(texto):
    """Busca 'ID: ' seguido de caracteres en el texto proporcionado."""
    match = re.search(r'ID:\s*(\S+)', texto)
    return match.group(1) if match else "No especificado"

@app.route('/api/send-order', methods=['POST'])
def send_order():
    data = request.json
    
    # Extraemos el ID del pedido desde la descripción/nombre del producto
    # Asumimos que viene en el campo 'producto_nombre' o podrías pasarlo en otro campo
    pedido_id = extraer_id(data.get('producto_nombre', ''))

    # 1. CONTENIDO PARA EL VENDEDOR (Tú)
    html_vendedor = f"""
    <h2>🚨 NUEVO PEDIDO RECIBIDO</h2>
    <p><b>ID del Producto:</b> {pedido_id}</p>
    <p><b>Producto:</b> {data['producto_nombre']}</p>
    <p><b>Precio:</b> {data['producto_precio']}</p>
    <hr>
    <h3>Datos del Cliente:</h3>
    <p><b>Nombre:</b> {data['nombre']}</p>
    <p><b>Teléfono:</b> {data['telefono']}</p>
    <p><b>Ubicación:</b> {data['ubicacion']}</p>
    <p><b>Email:</b> {data['correoCliente']}</p>
    """

    # 2. CONTENIDO PARA EL CLIENTE (Confirmación)
    html_cliente = f"""
    <h2>¡Gracias por tu pedido, {data['nombre']}!</h2>
    <p>Hemos recibido tu solicitud para el producto: <b>{data['producto_nombre']}</b></p>
    <p><b>ID de Referencia:</b> {pedido_id}</p>
    <p>En breve nos comunicaremos contigo al teléfono {data['telefono']} para coordinar la entrega.</p>
    <br>
    <p>Saludos,<br>Artesanías Maderex</p>
    """

    try:
        # ENVÍO AL VENDEDOR
        res_vendedor = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": "Artesanias Maderex <onboarding@resend.dev>",
                "to": VENDOR_EMAIL,
                "subject": f"NUEVO PEDIDO - ID: {pedido_id}",
                "html": html_vendedor,
            }
        )

        # ENVÍO AL CLIENTE (Solo si tienes el correo del cliente verificado o dominio propio)
        # Nota: En el modo prueba de Resend, esto podría fallar si el email del cliente no eres tú mismo.
        res_cliente = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}", "Content-Type": "application/json"},
            json={
                "from": "Artesanias Maderex <onboarding@resend.dev>",
                "to": data['correoCliente'],
                "subject": "Confirmación de tu pedido - Artesanías Maderex",
                "html": html_cliente,
            }
        )
        
        return jsonify({'success': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
