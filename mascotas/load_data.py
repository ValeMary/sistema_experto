import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
django.setup()

from mascotas.models import Sintoma, Enfermedad, PruebaDiagnostica, Prevencion

def cargar_datos():
    # Limpiar datos existentes
    Sintoma.objects.all().delete()
    Enfermedad.objects.all().delete()
    PruebaDiagnostica.objects.all().delete()

    # Cargar síntomas
    sintomas = [
        "Fiebre", "Presencia de garrapatas", "Letargo", "Depresión", "Anorexia",
        "Cojera", "Dolor articular", "Poliartritis", "Vómitos", "Diarrea",
        "Descoordinación", "Convulsiones", "Aumento del tamaño de los ganglios linfáticos",
        "Anemia", "Disminución del número de plaquetas", "Incremento de las enzimas hepáticas",
        "Palidez de mucosas", "Petequias", "Tos", "Uveítis", "Edemas",
        "Aumento en la ingesta de agua", "Pérdida de peso", "Coagulopatías",
        "Insuficiencia renal", "Problemas neurológicos"
    ]
    for nombre in sintomas:
        Sintoma.objects.create(nombre=nombre)

    # Cargar enfermedades con sus síntomas y pruebas diagnósticas
    enfermedades = [
        {
            "nombre": "Anaplasma platys",
            "sintomas": ["Fiebre", "Letargo", "Anorexia", "Disminución del número de plaquetas", "Petequias", "Cojera", "Dolor articular", "Pérdida de peso"],
            "tratamiento_recomendado": "Antibióticos (doxiciclina) durante 4 semanas.",
            "pruebas_diagnosticas": [
                "Examen físico completo",
                "Hemograma completo",
                "Frotis sanguíneo",
                "Prueba serológica (ELISA o inmunofluorescencia indirecta)",
                "PCR (reacción en cadena de la polimerasa)"
            ]
        },
        {
            "nombre": "Ehrlichia canis",
            "sintomas": ["Fiebre", "Letargo", "Anorexia", "Depresión", "Anemia", "Disminución del número de plaquetas", "Aumento del tamaño de los ganglios linfáticos", "Pérdida de peso", "Problemas neurológicos"],
            "tratamiento_recomendado": "Antibióticos (doxiciclina) durante 4 semanas, terapia de apoyo según sea necesario.",
            "pruebas_diagnosticas": [
                "Examen físico completo",
                "Hemograma completo",
                "Frotis sanguíneo",
                "Prueba serológica (ELISA o inmunofluorescencia indirecta)",
                "PCR (reacción en cadena de la polimerasa)",
                "Perfil bioquímico"
            ]
        },
        {
            "nombre": "Babesia canis",
            "sintomas": ["Fiebre", "Letargo", "Anorexia", "Anemia", "Disminución del número de plaquetas", "Palidez de mucosas", "Ictericia", "Pérdida de peso", "Coagulopatías", "Insuficiencia renal", "Problemas neurológicos"],
            "tratamiento_recomendado": "Antiparasitarios específicos (imidocarb o diminazeno), terapia de apoyo.",
            "pruebas_diagnosticas": [
                "Examen físico completo",
                "Hemograma completo",
                "Frotis sanguíneo",
                "Prueba serológica (ELISA o inmunofluorescencia indirecta)",
                "PCR (reacción en cadena de la polimerasa)",
                "Perfil bioquímico",
                "Urianálisis"
            ]
        },
    ]

    for enfermedad_data in enfermedades:
        enfermedad = Enfermedad.objects.create(
            nombre=enfermedad_data["nombre"],
            tratamiento_recomendado=enfermedad_data["tratamiento_recomendado"]
        )
        for sintoma_nombre in enfermedad_data["sintomas"]:
            sintoma, _ = Sintoma.objects.get_or_create(nombre=sintoma_nombre)
            enfermedad.sintomas.add(sintoma)
        
        for prueba_nombre in enfermedad_data["pruebas_diagnosticas"]:
            prueba, _ = PruebaDiagnostica.objects.get_or_create(nombre=prueba_nombre)
            enfermedad.pruebas_diagnosticas.add(prueba)

    # Cargar prevenciones separadamente
    prevenciones = {
        "Anaplasma platys": [
            "Control de garrapatas",
            "Inspección regular",
            "Uso de antiparasitarios"
        ],
        "Ehrlichia canis": [
            "Uso de productos anti-garrapatas",
            "Inspección frecuente",
            "Eliminación rápida de garrapatas",
            "Mantenimiento del césped corto",
            "Evitar áreas con alta presencia de garrapatas",
            "Vacunación (si está disponible)"
        ],
        "Babesia canis": [
            "Control de garrapatas",
            "Inspección regular",
            "Remoción rápida de garrapatas",
            "Evitar áreas infestadas",
            "Mantenimiento del entorno limpio",
            "Uso de repelentes",
            "Vacunación en áreas endémicas (si está disponible)"
        ]
    }

    for enfermedad_nombre, prevenciones_lista in prevenciones.items():
        enfermedad = Enfermedad.objects.get(nombre=enfermedad_nombre)
        for prevencion_desc in prevenciones_lista:
            prevencion, _ = Prevencion.objects.get_or_create(descripcion=prevencion_desc)
            enfermedad.prevenciones.add(prevencion)
    sintomas_comunes = {
        "todas": ["Fiebre", "Letargo", "Anemia", "Pérdida de peso"],
        "Anaplasma platys y Ehrlichia canis": ["Fiebre", "Letargo", "Anemia", "Pérdida de apetito", "Cojera", "Dolor articular", "Petequias", "Aumento del tamaño de los ganglios linfáticos"],
        "Anaplasma platys y Babesia canis": ["Fiebre", "Anemia", "Letargo", "Pérdida de peso", "Coagulopatías", "Insuficiencia renal"],
        "Ehrlichia canis y Babesia canis": ["Fiebre", "Letargo", "Anemia", "Pérdida de peso", "Problemas neurológicos"]
    }

    for categoria, sintomas in sintomas_comunes.items():
        for sintoma_nombre in sintomas:
            sintoma, _ = Sintoma.objects.get_or_create(nombre=sintoma_nombre)
            if categoria == "todas":
                for enfermedad in Enfermedad.objects.all():
                    enfermedad.sintomas.add(sintoma)
            else:
                enfermedades_nombres = categoria.split(" y ")
                for enfermedad_nombre in enfermedades_nombres:
                    enfermedad = Enfermedad.objects.get(nombre=enfermedad_nombre)
                    enfermedad.sintomas.add(sintoma)

    print("Datos cargados exitosamente, incluyendo síntomas comunes entre enfermedades.")

if __name__ == "__main__":
    cargar_datos()