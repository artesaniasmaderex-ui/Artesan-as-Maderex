from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests # Esta librería es la que envía el mail por "atrás"

base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_folder=base_dir)
CORS(app)

# Configuración de Resend
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
VENDOR_EMAIL = 'elifalero2013@gmail.com'

@app.route('/')
def serve_index():
    return send_from_directory(base_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(base_dir, path)

@app.route('/api/send-order', methods=['POST'])
def send_order():
    data = request.json
    
    # Contenido del correo que te llegará a ti
    email_content = f"""
    <h2>🚨 Nuevo Pedido: {data['producto_nombre']}</h2>
    <p><b>Cliente:</b> {data['nombre']}</p>
    <p><b>Teléfono:</b> {data['telefono']}</p>
    <p><b>Ubicación:</b> {data['ubicacion']}</p>
    <p><b>Precio:</b> {data['producto_precio']}</p>
    <p><b>Email cliente:</b> {data['correoCliente']}</p>
    """

    try:
        # Petición a la API de Resend
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": "Artesanias Maderex <onboarding@resend.dev>",
                "to": VENDOR_EMAIL,
                "subject": f"Pedido: {data['producto_nombre']}",
                "html": email_content,
            }
        )
        
        if response.status_code in [200, 201]:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'error': 'Error en la API de Resend'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
