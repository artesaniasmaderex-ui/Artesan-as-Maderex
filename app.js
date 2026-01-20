// 1. Manejo del carrusel de fotos horizontal
function scrollFotos(btn, direccion) {
    const contenedor = btn.parentElement.querySelector('.fotos-wrapper');
    const anchoFoto = contenedor.clientWidth;
    contenedor.scrollBy({
        left: direccion * anchoFoto,
        behavior: 'smooth'
    });
}

// 2. Función para volver al primer post
function irArriba() {
    const container = document.querySelector('.tiktok-container');
    if (container) {
        container.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }
}

// 3. Gestión de datos de compra
let datosProductoSeleccionado = {};

// 4. Abrir panel de detalles
function abrirDetalles(boton) {
    const post = boton.closest('.post');
    const nombre = post.querySelector('.p-name').textContent;
    const precio = post.querySelector('.p-price').textContent;
    const detalles = post.querySelector('.p-details').textContent;
    const imagen = post.querySelector('img').src;

    // Llenar el modal con la info del post actual
    document.getElementById('modalImg').src = imagen;
    document.getElementById('modalName').textContent = nombre;
    document.getElementById('modalPrice').textContent = precio;
    document.getElementById('modalDetails').textContent = detalles;

    // Guardar para el paso final
    datosProductoSeleccionado = { nombre, precio, imagen };

    document.getElementById('modalBackdrop').classList.add('active');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('active');
}

function openFormModal() {
    closeModal('modalBackdrop');
    // Llenar resumen del formulario
    document.getElementById('summaryImg').src = datosProductoSeleccionado.imagen;
    document.getElementById('summaryName').textContent = datosProductoSeleccionado.nombre;
    document.getElementById('summaryPrice').textContent = datosProductoSeleccionado.precio;
    
    document.getElementById('formBackdrop').classList.add('active');
}

// 5. Envío del formulario al servidor Python en RENDER
document.getElementById('purchaseForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const mensaje = document.getElementById('message');
    mensaje.textContent = 'Enviando pedido...';
    mensaje.style.color = 'orange';

    const formData = new FormData(e.target);
    const payload = {
        ...Object.fromEntries(formData.entries()),
        producto_nombre: datosProductoSeleccionado.nombre,
        producto_precio: datosProductoSeleccionado.precio,
        producto_imagen: datosProductoSeleccionado.imagen // Agregado para que el mail tenga la foto
    };

    try {
        // CAMBIO AQUÍ: Ahora apunta a RENDER en lugar de localhost
        const response = await fetch('https://artesan-as-maderex.onrender.com/api/send-order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        if (response.ok) {
            mensaje.textContent = '✅ ¡Pedido enviado con éxito!';
            mensaje.style.color = 'green';
            setTimeout(() => {
                closeModal('formBackdrop');
                e.target.reset();
                mensaje.textContent = '';
            }, 3000);
        } else {
            // Muestra el error específico que devuelve Flask si falla el mail
            mensaje.textContent = '❌ Error: ' + (result.error || 'No se pudo enviar');
            mensaje.style.color = 'red';
        }
    } catch (error) {
        mensaje.textContent = '❌ Error de conexión con el servidor.';
        mensaje.style.color = 'red';
        console.error("Error en el fetch:", error);
    }
});
