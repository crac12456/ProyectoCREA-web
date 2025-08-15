document.addEventListener("DOMContentLoaded", function() {
    let labels = [];
    let phData = [];
    let turbidezData = [];
    let tempData = [];

    // Función para crear configuración de Chart.js
    const createConfig = (label, data, color) => ({
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: 'rgba(0,0,0,0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { 
                    title: { display: true, text: 'Tiempo' } 
                },
                y: { 
                    title: { display: true, text: label } 
                }
            }
        }
    });

    // Crear gráficos
    const phChart = new Chart(document.getElementById('phChart'), createConfig('pH', phData, 'red'));
    const turbidezChart = new Chart(document.getElementById('turbidezChart'), createConfig('Turbidez', turbidezData, 'blue'));
    const tempChart = new Chart(document.getElementById('tempChart'), createConfig('Temperatura', tempData, 'green'));

    // Función para actualizar valores y gráficos
    function updateCharts(ph, turbidez, temp) {
        const time = new Date().toLocaleTimeString();
        labels.push(time);
        phData.push(ph);
        turbidezData.push(turbidez);
        tempData.push(temp);

        // Mantener últimos 20 puntos
        if (labels.length > 20) {
            labels.shift();
            phData.shift();
            turbidezData.shift();
            tempData.shift();
        }

        // Actualizar <li> con valores
        document.getElementById('phValue').textContent = ph;
        document.getElementById('turbidezValue').textContent = turbidez;
        document.getElementById('tempValue').textContent = temp;

        phChart.update();
        turbidezChart.update();
        tempChart.update();
    }

    // Simulación de datos (reemplaza luego con tu API o Flask)
    setInterval(() => {
        const ph = (6 + Math.random()*2).toFixed(2);
        const turbidez = (10 + Math.random()*10).toFixed(2);
        const temp = (20 + Math.random()*5).toFixed(2);
        updateCharts(ph, turbidez, temp);
    }, 2000);
});
