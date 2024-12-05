  // Función para obtener datos de la API y procesarlos
  async function fetchApiData() {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/syserrors/');
      if (!response.ok) throw new Error('Error en la solicitud');

      const data = await response.json();
      console.log('Solicitud de get exitosa', data);

      // Procesar datos para la gráfica de Status Sites (errores por fecha)
      const errorDates = data.map(item => item.date_error);
      const uniqueDates = [...new Set(errorDates)];
      const errorsCount = uniqueDates.map(date => errorDates.filter(d => d === date).length);

      // Crear gráfica Status Sites
   // Crear gráfica Status Sites
const ctxStatusSites = document.getElementById('statusSitesChart').getContext('2d');
new Chart(ctxStatusSites, {
  type: 'line',
  data: {
    labels: uniqueDates,
    datasets: [{
      label: 'Errores por Fecha',
      data: errorsCount,
      borderColor: '#F44336',
      backgroundColor: 'rgba(244, 67, 54, 0.2)',
      fill: false, 
      borderWidth: 2,
      pointRadius: 0, 
      pointHoverRadius: 0, 
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        title: {
          display: true,
          text: 'Fecha',
        },
        grid: {
          display: false,
        },
      },
      y: {
        min: 0,
        max: 1,
        title: {
          display: true,
          text: 'Número de Errores',
        },
        grid: {
          drawBorder: false,
          color: 'rgba(0, 0, 0, 0.1)',
          lineWidth: 1,
        },
        ticks: {
          beginAtZero: true, 
          fontSize: 12,
          fontColor: '#97a4af',
          fontFamily: 'Open Sans, sans-serif',
          padding: 20,
        },
      },
    },
    animations: {
      tension: {
        duration: 1000,
        easing: 'linear',
        from: 1,
        to: 0,
        loop: true,
      }
    },
    legend: {
      display: false, 
    },
    tooltips: {
      intersect: false, 
      mode: 'index',
    },
  },
});


      // Procesar datos para la gráfica de Server Status (sitios más caídos)
      const siteUrls = data.map(item => item.site_url);
      const siteUrlCount = siteUrls.reduce((acc, url) => {
        acc[url] = (acc[url] || 0) + 1;
        return acc;
      }, {});

      const siteLabels = Object.keys(siteUrlCount);
      const siteCounts = Object.values(siteUrlCount);

      // Crear gráfica Server Status
const ctxServerStatus = document.getElementById('polarAreaChart').getContext('2d');
new Chart(ctxServerStatus, {
  type: 'doughnut',  // Cambié de polarArea a doughnut
  data: {
    labels: siteLabels,  // Usar las URLs de los sitios como etiquetas
    datasets: [{
      label: 'Errores por Sitio',
      data: siteCounts,  // Contador de errores por sitio
      backgroundColor: ['#FF5733', '#FFC300', '#DAF7A6', '#C70039', '#581845'],  // Colores de fondo
      hoverBackgroundColor: ['#FF5733', '#FFC300', '#DAF7A6', '#C70039', '#581845'],  // Colores al pasar el mouse
      borderWidth: 0,  // Sin borde
      weight: 0.5,  // Grosor del gráfico
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    legend: {
      position: 'bottom',  // Leyenda en la parte inferior
    },
    title: {
      display: false,  // No mostrar título
    },
    animation: {
      animateScale: true,  // Animación de escala al cargar
      animateRotate: true,  // Animación de rotación al cargar
    },
  }
});

      // Mostrar detalles en el div
      const errorDetails = document.getElementById('errorDetails');
      const errorRows = data.map(item => `
        <tr>
          <td class="px-4 py-2 text-gray-700 border-b dark:text-light">${item.site_url}</td>
          <td class="px-4 py-2 text-gray-600 border-b dark:text-light">${item.date_error}</td>
          <td class="px-4 py-2 text-gray-600 border-b dark:text-light">${item.error_site_code}</td>
        </tr>
      `).join('');
      
      errorDetails.querySelector('tbody').innerHTML = errorRows;

    } catch (error) {
      console.error('Error de la solicitud del get:', error);
    }
  }

  // Llamar a la función al cargar la página
  window.onload = fetchApiData;

  // Funcionalidad para alternar el sidebar en dispositivos móviles
  const sidebarToggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');

  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('hidden');
    mainContent.classList.toggle('ml-0');
  });
  const networkStatusChart = new Chart(document.getElementById('networkStatusChart'), {
  type: 'bar',
  data: {
    // Las etiquetas representan los diferentes estados de la red
    labels: ['Online', 'Offline'],
    datasets: [
      {
        label: 'Estado de la Red',
        data: [70, 30], // Puedes reemplazar estos valores con tus datos reales
        backgroundColor: ['#4caf50', '#f44336'], // Verde para Online, Rojo para Offline
        borderWidth: 0,
        categoryPercentage: 1,
      },
    ],
  },
  options: {
    scales: {
      y: {
        beginAtZero: true, // Comienza desde cero
        grid: {
          display: false, // No mostrar las líneas de la cuadrícula
        },
      },
      x: {
        grid: {
          display: false, // No mostrar las líneas de la cuadrícula
        },
      },
    },
    cornerRadius: 2,
    maintainAspectRatio: false, // Hace que la gráfica sea responsiva
    legend: {
      display: false, // Ocultar la leyenda
    },
    tooltips: {
      callbacks: {
        label: function (tooltipItem) {
          return tooltipItem.raw + '%'; // Muestra el porcentaje al pasar el cursor
        },
      },
    },
    hover: {
      mode: 'nearest',
      intersect: true,
    },
  },
});
