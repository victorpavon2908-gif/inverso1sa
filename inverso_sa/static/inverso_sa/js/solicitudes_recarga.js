// Abrir modal
function openModal(id) {
    document.getElementById('modal-' + id).style.display = 'block';
}

// Cerrar modal
function closeModal(id) {
    document.getElementById('modal-' + id).style.display = 'none';
}

// Cerrar modal al hacer click fuera del contenido
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}
