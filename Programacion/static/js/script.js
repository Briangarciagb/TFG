// Función para mostrar/ocultar sidebar
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  sidebar.classList.toggle('active');
}

// Escuchar eventos cuando cargue la página
document.addEventListener("DOMContentLoaded", function () {
  console.log("Script cargado correctamente...");

  // --- Manejo del sidebar ---
  const sidebar = document.getElementById('sidebar');
  if (sidebar) {
    const menuButton = document.querySelector(".hamburger-menu");
    if (menuButton) {
      menuButton.addEventListener("click", toggleSidebar);
    }
  }

  // --- Lógica para el botón de configuración ---
  const configButton = document.querySelector(".config-btn");
  if (configButton) {
    configButton.addEventListener("click", function () {
      console.log("Redirigiendo a la página de configuración...");
      window.location.href = "/configuracion"; // Redirige a la página de configuración
    });
  } else {
    console.warn("⚠️ No se encontró el botón de configuración en esta página.");
  }

  // --- Botón "Recargar API" en la página Principal (si existe) ---
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

  // --- Lógica para la página fitness ---
  const fitnessDataTable = document.getElementById("fitnessDataTable");
  if (fitnessDataTable) {
    console.log("Fitness table encontrada. Cargando datos...");
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
