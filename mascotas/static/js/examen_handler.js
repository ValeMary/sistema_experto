// examen_handler.js
class ExamenHandler {
    constructor() {
        this.cargarExamenBtn = document.getElementById('cargarExamen');
        this.init();
    }

    init() {
        if (this.cargarExamenBtn) {
            this.cargarExamenBtn.addEventListener('click', this.handleCargarExamen.bind(this));
        } else {
            console.error("El botón 'Cargar Examen' no fue encontrado");
        }
    }

    handleCargarExamen(e) {
        e.preventDefault();
        console.log("Botón Cargar Examen clickeado");

        const mascotaId = this.cargarExamenBtn.dataset.mascotaId;
        console.log("ID de la mascota:", mascotaId);

        if (!mascotaId) {
            console.error("ID de mascota no disponible");
            return;
        }

        const url = `/mascotas/${mascotaId}/cargar-examen/`;
        console.log("cargar_examen:", url);

        window.location.href = url;
    }
}

// Exporta la clase para que pueda ser importada en otros archivos
export default ExamenHandler;