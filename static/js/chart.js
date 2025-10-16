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
                    title: { display: true, text: label },
                    min: label === 'Temperatura' ? 10 : (label === 'pH' ? 4 : 0),
                    max: label === 'Temperatura' ? 30 : (label === 'pH' ? 12 : 50)
                }
            }
        }
    });

    // Crear gráficos
    const phChart = new Chart(document.getElementById('phChart'), createConfig('pH', phData, 'red'));
    const turbidezChart = new Chart(document.getElementById('turbidezChart'), createConfig('Turbidez', turbidezData, 'blue'));
    const tempChart = new Chart(document.getElementById('tempChart'), createConfig('Temperatura', tempData, 'green'));

    function updateCharts(ph, turbidez, temp) {
        const time = new Date().toLocaleTimeString();
        labels.push(time);

        const safePh = (ph === null || ph === undefined) ? 0 : parseFloat(ph);
        const safeTurbidez = (turbidez === null || turbidez === undefined) ? 0 : parseFloat(turbidez);
        const safeTemp = (temp === null || temp === undefined) ? 0 : parseFloat(temp);

        phData.push(safePh);
        turbidezData.push(safeTurbidez);
        tempData.push(safeTemp);

        if (labels.length > 20) {
            labels.shift();
            phData.shift();
            turbidezData.shift();
            tempData.shift();
        }

        document.getElementById('phValue').textContent = safePh.toFixed(2);
        document.getElementById('turbidezValue').textContent = safeTurbidez.toFixed(2);
        document.getElementById('tempValue').textContent = safeTemp.toFixed(2);

        phChart.update();
        turbidezChart.update();
        tempChart.update();
    }

    // 🔹 Simulación mejorada de pH (más natural)
    let simularPH = true; // Cambia a false si conectas el sensor real
    let phSimulado = 7.0; // Valor base
    function obtenerPHSimulado() {
        // Pequeñas variaciones aleatorias suaves (sube o baja ligeramente)
        let cambio = (Math.random() - 0.5) * 0.1; // ±0.05 aprox
        phSimulado += cambio;

        // Limitar entre 6.5 y 8.0
        if (phSimulado > 8.0) phSimulado = 8.0;
        if (phSimulado < 6.5) phSimulado = 6.5;

        return phSimulado.toFixed(2);
    }

    async function updateTable() {
        try {
            const response = await fetch("api/datos");
            const data = await response.json();
            const tbody = document.querySelector('#datosHistoricosTable tbody');
            
            if (tbody) {
                tbody.innerHTML = ''; 
                data.slice(0, 10).forEach(row => {
                    const tr = document.createElement('tr');
                    const date = new Date(row.timestamp);
                    const timeStr = date.toLocaleTimeString();

                    tr.innerHTML = `
                        <td>${row.id}</td>
                        <td>${timeStr}</td>
                        <td>${row.dispositivo}</td>
                        <td>${(row.temperatura || 0).toFixed(2)}</td>
                        <td>${(row.ph || 0).toFixed(2)}</td>
                        <td>${(row.turbidez || 0).toFixed(2)}</td>
                    `;
                    tbody.appendChild(tr);
                });
            }
        } catch (error) {
            console.error("Error obteniendo datos históricos:", error);
        }
    }

    // 🔹 Actualización de gráficos en vivo
    setInterval(async () => {
        try {
            const response = await fetch("api/ultimo");
            const data = await response.json();

            // Si simulamos, solo el pH se reemplaza por el simulado
            const phReal = simularPH ? obtenerPHSimulado() : data.ph;

            updateCharts(phReal, data.turbidez, data.temperatura);
        } catch (error) {
            console.error("Error obteniendo datos en vivo:", error);
        }
    }, 2000);

    // 🔹 Actualización periódica de tabla
    setInterval(updateTable, 10000);
    updateTable(); // Llamada inicial
});
