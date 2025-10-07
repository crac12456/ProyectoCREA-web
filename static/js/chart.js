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

    // Obtener datos reales desde Flask cada 3 segundos
    setInterval(async () => {
        try {
            const response = await fetch("api/datos");
            const data = await response.json();

            updateCharts(data.ph, data.turbidez, data.temperatura);
        } catch (error) {
            console.error("Error obteniendo datos:", error);
        }
    }, 3000);
});
