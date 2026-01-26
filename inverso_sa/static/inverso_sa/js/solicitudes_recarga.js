function openModal(id) {
    const modal = document.getElementById("modal-" + id);
    modal.classList.add("show");
}

function closeModal(id) {
    const modal = document.getElementById("modal-" + id);
    modal.classList.remove("show");
}

window.addEventListener("click", function (e) {
    if (e.target.classList.contains("modal")) {
        e.target.classList.remove("show");
    }
});
