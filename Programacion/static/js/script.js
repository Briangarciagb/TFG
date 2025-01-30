// Mostrar/ocultar sidebar
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('active');
}

// Escuchar eventos cuando cargue la página
document.addEventListener("DOMContentLoaded", function () {
  // Botón "Recargar API" en la página Principal (si existe)
  const refreshButton = document.getElementById("refreshApiButton");
  const statusMessage = document.getElementById("statusMessage");
  
  if (refreshButton && statusMessage) {
    refreshButton.addEventListener("click", function () {
      const hoy = new Date().toISOString().split("T")[0];
      statusMessage.textContent = "Llamando a la API...";

      fetch("/datos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fecha: hoy })
      })
        .then(response => response.json())
        .then(data => {
          if (data.status === "success") {
            statusMessage.textContent =
              `Datos cargados:
               Pasos=${data.data.pasos},
               Calorías=${data.data.calorias},
               Distancia=${data.data.distancia} km,
               Sueño=${data.data.sueno} h`;
          } else {
            statusMessage.textContent = "Error: " + data.message;
          }
        })
        .catch(error => {
          console.error("Error en la solicitud:", error);
          statusMessage.textContent = "Error en la solicitud";
        });
    });
  }

  // --- LÓGICA PARA LA PÁGINA FITNESS ---
  // Si estamos en "fitness.html", busca el elemento con id="fitnessDataTable"
  const fitnessDataTable = document.getElementById("fitnessDataTable");
  if (fitnessDataTable) {
    // Automáticamente cargamos la fecha de hoy (puedes permitir que el usuario elija)
    const hoy = new Date().toISOString().split("T")[0];
    
    fetch("/datos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fecha: hoy })
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === "success") {
          const { pasos, calorias, distancia, sueno } = data.data;
          // Rellenar la tabla
          fitnessDataTable.innerHTML = `
            <tr>
              <th>Pasos</th>
              <th>Calorías</th>
              <th>Distancia (km)</th>
              <th>Sueño (horas)</th>
            </tr>
            <tr>
              <td>${pasos}</td>
              <td>${calorias}</td>
              <td>${distancia}</td>
              <td>${sueno}</td>
            </tr>
          `;
        } else {
          fitnessDataTable.innerHTML = `
            <tr>
              <td colspan="4">Error: ${data.message}</td>
            </tr>
          `;
        }
      })
      .catch(error => {
        console.error("Error en la solicitud:", error);
        fitnessDataTable.innerHTML = `
          <tr>
            <td colspan="4">Error al obtener datos</td>
          </tr>
        `;
      });
  }
});
