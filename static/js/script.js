// Objeto para rastrear teclas presionadas
const pressedKeys = {};

// Escucha teclado
document.addEventListener("keydown", function(event) {
    let key = event.key.toLowerCase();

    if (["w","a","s","d"].includes(key) && !pressedKeys[key]) {
        pressedKeys[key] = true;

        // Enviar la tecla al servidor Flask
        fetch(`/control/${key}`, { method: "POST" })
            .then(response => response.text())
            .then(data => console.log("Servidor:", data));

        // Activar animación permanente mientras se mantenga presionada
        let btn = document.querySelector(`.btn-control[data-key="${key}"]`);
        if (btn) btn.classList.add("active");
    }
});

// Escucha cuando se suelta la tecla
document.addEventListener("keyup", function(event) {
    let key = event.key.toLowerCase();

    if (["w","a","s","d"].includes(key)) {
        pressedKeys[key] = false;

        // Quitar animación
        let btn = document.querySelector(`.btn-control[data-key="${key}"]`);
        if (btn) btn.classList.remove("active");
    }
});

// Escucha clic en botones
document.querySelectorAll(".btn-control").forEach(btn => {
    btn.addEventListener("click", function() {
        let key = this.getAttribute("data-key");

        // Enviar al servidor
        fetch(`/control/${key}`, { method: "POST" })
            .then(r => r.text())
            .then(data => console.log("Servidor:", data));

        // Animación temporal de clic
        this.classList.add("active");
        setTimeout(() => this.classList.remove("active"), 200);
    });
});