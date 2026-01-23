function openModal(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) {
        modal.classList.add("show");
    }
}

function closeModal(id) {
    const modal = document.getElementById("modal-" + id);
    if (modal) {
        modal.classList.remove("show");
    }
}

window.addEventListener("click", function (e) {
    if (e.target.classList.contains("modal")) {
        e.target.classList.remove("show");
    }
});
