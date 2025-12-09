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
                        min: label === 'Temperatura' ? 10 : 0, // 👈 Arranca en 10 si es temperatura
                        max: label === 'Temperatura' ? 30 : (label === 'pH' ? 14 : 50)
    }
}

        }
    });

    // Crear gráficos
    const phChart = new Chart(document.getElementById('phChart'), createConfig('pH', phData, 'red'));
    const turbidezChart = new Chart(document.getElementById('turbidezChart'), createConfig('Turbidez', turbidezData, 'blue'));
    const tempChart = new Chart(document.getElementById('tempChart'), createConfig('Temperatura', tempData, 'green'));

    // Función para actualizar valores y gráficos
    // CORRECCIÓN: Los argumentos son ahora 'ph', 'turbidez', 'temp'
    function updateCharts(ph, turbidez, temp) {
        const time = new Date().toLocaleTimeString();
        labels.push(time);
        
        // Uso de valores con fallback a 0 y redondeo a 2 decimales
        const safePh = (ph === null || ph === undefined) ? 0 : parseFloat(ph);
        const safeTurbidez = (turbidez === null || turbidez === undefined) ? 0 : parseFloat(turbidez);
        const safeTemp = (temp === null || temp === undefined) ? 0 : parseFloat(temp);
        
        phData.push(safePh);
        turbidezData.push(safeTurbidez);
        tempData.push(safeTemp);

        // Mantener últimos 20 puntos
        if (labels.length > 20) {
            labels.shift();
            phData.shift();
            turbidezData.shift();
            tempData.shift();
        }

        // Actualizar <li> con valores
        document.getElementById('phValue').textContent = safePh.toFixed(2);
        document.getElementById('turbidezValue').textContent = safeTurbidez.toFixed(2);
        document.getElementById('tempValue').textContent = safeTemp.toFixed(2);

        phChart.update();
        turbidezChart.update();
        tempChart.update();
    }
    
    // Nueva función para actualizar la tabla histórica (usa /api/datos)
    async function updateTable() {
        try {
            const response = await fetch("api/datos"); // Obtiene los 100 registros
            const data = await response.json();
            const tbody = document.querySelector('#datosHistoricosTable tbody');
            
            if (tbody) { // Solo si la tabla existe en el HTML
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


    // Obtener datos reales desde Flask cada 3 segundos (ACTUALIZACIÓN DE GRÁFICAS)
    setInterval(async () => {
        try {
            const response = await fetch("api/ultimo"); // Correcto: Trae el último dato
            const data = await response.json();

            // CORRECCIÓN CRÍTICA: Usar data.ph, data.turbidez, data.temperatura
            updateCharts(data.ph, data.turbidez, data.temperatura);
        } catch (error) {
            console.error("Error obteniendo datos en vivo:", error);
        }
    }, 2000);
    
    // Llamadas a la tabla histórica
    setInterval(updateTable, 10000);
    updateTable(); // Llamada inicial
});