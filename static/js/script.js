// Objeto para rastrear teclas presionadas
const pressedKeys = {};

// Escucha teclado
document.addEventListener("keydown", function(event) {
    let key = event.key;

    // Convertir a minúscula si no es espacio
    if(key !== " ") key = key.toLowerCase();

    if (["w","a","s","d"," "].includes(key) && !pressedKeys[key]) {
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
    let key = event.key;
    if(key !== " ") key = key.toLowerCase();

    if (["w","a","s","d"," "].includes(key)) {
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
document.addEventListener("DOMContentLoaded", () => {
    const track = document.querySelector(".carousel-track-multi");
    const images = document.querySelectorAll(".carousel-track-multi img");

    let index = 0;
    const visible = 3;              // cantidad de imágenes visibles a la vez
    const total = images.length;

    function update() {
        const imgWidth = images[0].clientWidth + 15; // ancho + gap
        track.style.transform = `translateX(${-index * imgWidth}px)`;
    }

    document.querySelector(".cbtn.next").addEventListener("click", () => {
        if (index < total - visible) index++;
        update();
    });

    document.querySelector(".cbtn.prev").addEventListener("click", () => {
        if (index > 0) index--;
        update();
    });

    window.addEventListener("resize", update);
});
