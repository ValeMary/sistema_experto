
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
import re
import csv
from django.utils import timezone
from django.urls import reverse
from .forms import MascotaForm
from .models import Sintoma, Enfermedad, Mascota, Prevencion, PruebaDiagnostica, ExamenMascota
from mascotas.model import ModeloIA
from django.template.loader import render_to_string
import nltk
from django.views.decorators.http import require_POST
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
 
import PyPDF2
 
@require_POST
def guardar_sintomas(request, mascota_nombre):
    try:
        mascota = Mascota.objects.get(nombre=mascota_nombre)
        sintomas_ids = request.POST.getlist('sintomas')
        
        # Elimina los síntomas anteriores de la mascota
        mascota.sintomas.clear()
        
        # Agrega los nuevos síntomas seleccionados
        sintomas = Sintoma.objects.filter(id__in=sintomas_ids)
        mascota.sintomas.add(*sintomas)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def sintomas_mascota(request, mascota_nombre):
    mascota = get_object_or_404(Mascota, nombre=mascota_nombre)
    sintomas = Sintoma.objects.all()
    return render(request, 'mascotas/sintomas.html', {
        'mascota_nombre': mascota_nombre,
        'sintomas': sintomas,
        'sintomas_seleccionados': mascota.sintomas.all()
    })
#---------------------------------------------------------------------



from django.shortcuts import render, redirect, get_object_or_404
from .forms import MascotaForm
from .models import Sintoma, Enfermedad, PruebaDiagnostica, Prevencion, Mascota, Tratamiento
from .model import ModeloIA
from django.utils import timezone
from django.shortcuts import render, redirect
from django.utils import timezone
from .forms import MascotaForm
from .models import Sintoma, Enfermedad, Tratamiento
from .model import ModeloIA

# Crear una instancia global del modelo
modelo_ia = ModeloIA()

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def registro_mascota(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            mascota = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'mascota_nombre': mascota.nombre
                })
            else:
                return redirect('mascotas:detalle_mascota', mascota_nombre=mascota.nombre)
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': form.errors.as_json()
                })
    else:
        form = MascotaForm()
    
    return render(request, 'mascotas/registro_mascota.html', {'form': form})

########################################################################
def generar_tratamiento(enfermedades):
    tratamiento = "Tratamiento recomendado:\n"
    for enfermedad in enfermedades:
        if enfermedad.nombre == "Anaplasma platys":
            tratamiento += f"- Para {enfermedad.nombre}:\n"
            tratamiento += " • Antibióticos (doxiciclina) durante 4 semanas\n"
            tratamiento += " • Monitoreo de recuento de plaquetas\n"
            tratamiento += " • Terapia de apoyo para manejar síntomas\n"
            tratamiento += " • Control de garrapatas\n"
        elif enfermedad.nombre == "Ehrlichia canis":
            tratamiento += f"- Para {enfermedad.nombre}:\n"
            tratamiento += " • Doxiciclina durante 4 semanas\n"
            tratamiento += " • Terapia de apoyo según los síntomas\n"
            tratamiento += " • Monitoreo de recuento sanguíneo\n"
            tratamiento += " • Control de garrapatas\n"
        elif enfermedad.nombre == "Babesia canis":
            tratamiento += f"- Para {enfermedad.nombre}:\n"
            tratamiento += " • Antiprotozoarios específicos (imidocarb o atovacuona)\n"
            tratamiento += " • Terapia de apoyo, posible transfusión de sangre si es necesario\n"
            tratamiento += " • Monitoreo de parámetros sanguíneos\n"
            tratamiento += " • Control de garrapatas\n"
        else:
            tratamiento += f"- Para {enfermedad.nombre}: {enfermedad.tratamiento_recomendado}\n"
    
    tratamiento += "\nNota: Este tratamiento es una recomendación general. Consulte siempre con un veterinario para un diagnóstico y tratamiento específico."
    return tratamiento
#--------------------------------------------------------------------------#
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
 
from .predictor import EnfermedadPredictor

from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .models import Sintoma


@require_http_methods(["GET", "POST"])
def prediccion_enfermedad(request, mascota_nombre):
    print("Entrando a la vista prediccion_enfermedad")
    print(f"Nombre de la mascota recibido: {mascota_nombre}")

    try:
        sintomas = Sintoma.objects.all().order_by('nombre')
        print(f"Número de síntomas cargados: {sintomas.count()}")
    except Exception as e:
        print(f"Error al cargar síntomas: {str(e)}")
        sintomas = []

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            return procesar_prediccion_ajax(request, mascota_nombre)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            print(f"Error en procesar_prediccion_ajax: {str(e)}")
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)

    context = {
        'sintomas': sintomas,
        'mascota_nombre': mascota_nombre
    }
    print("Contexto preparado, intentando renderizar template")
    return render(request, 'mascotas/prediccion_resultado.html', context)
 
###################################################################################
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from collections import Counter
from .models import Sintoma, Enfermedad

def procesar_prediccion_ajax(request, mascota_nombre):
    sintomas_ids = request.POST.getlist('sintomas')
    sintomas_seleccionados = Sintoma.objects.filter(id__in=sintomas_ids)
    sintomas_texto = ", ".join([s.nombre for s in sintomas_seleccionados])

    # Obtener todas las enfermedades relacionadas con los síntomas seleccionados
    enfermedades_relacionadas = Enfermedad.objects.filter(sintomas__in=sintomas_seleccionados).distinct()

    # Contar cuántas veces aparece cada enfermedad
    conteo_enfermedades = Counter()
    for sintoma in sintomas_seleccionados:
        for enfermedad in sintoma.enfermedad_set.all():
            conteo_enfermedades[enfermedad] += 1

    # Preparar la lista de enfermedades posibles con sus conteos
    enfermedades_posibles = [
        {
            'enfermedad': enfermedad,
            'conteo': conteo,
            'porcentaje': (conteo / len(sintomas_seleccionados)) * 100
        }
        for enfermedad, conteo in conteo_enfermedades.items()
    ]

    # Ordenar las enfermedades por conteo de síntomas, de mayor a menor
    enfermedades_posibles.sort(key=lambda x: x['conteo'], reverse=True)

    # Encontrar la enfermedad con más síntomas coincidentes
    if enfermedades_posibles:
        enfermedad_predicha = enfermedades_posibles[0]['enfermedad']
        conteo_max = enfermedades_posibles[0]['conteo']
        total_sintomas = len(sintomas_seleccionados)

        prevenciones = enfermedad_predicha.prevenciones.all()
        pruebas_diagnosticas = enfermedad_predicha.pruebas_diagnosticas.all()

        resultado_context = {
            'enfermedad_predicha': enfermedad_predicha,
            'prevenciones': prevenciones,
            'pruebas_diagnosticas': pruebas_diagnosticas,
            'sintomas_texto': sintomas_texto,
            'mascota_nombre': mascota_nombre,
            'conteo_sintomas': conteo_max,
            'total_sintomas': total_sintomas,
            'enfermedades_posibles': enfermedades_posibles
        }

        html_resultado = render_to_string('mascotas/resultado_prediccion.html', resultado_context)
        return JsonResponse({'html_resultado': html_resultado})
    else:
        return JsonResponse({'mensaje': 'No se encontraron enfermedades relacionadas con los síntomas seleccionados.'})
############################################################################################
def obtener_enfermedades_posibles(sintomas_seleccionados):
    enfermedades_info = {
        "Anaplasma platys": {
            "sintomas": [
                "Fiebre", "Presencia de garrapatas", "Letargo", "Depresión", "Anorexia",
                  "Dolor articular", "Poliartritis", "Vómitos", "Diarrea",
                "Descoordinación", "Convulsiones", "Aumento del tamaño de los ganglios linfáticos",
                "Anemia", "Disminución del número de plaquetas", "Incremento de las enzimas hepáticas",
                "Palidez de mucosas", "Petequias", "Tos", "Uveítis", "Edemas",
                "Aumento en la ingesta de agua", "Trombocitopenia cíclica", "Sangrado excesivo",
                "Pérdida de peso", "Ictericia", "Hematomas", "Sangrado nasal", "Sangre en heces",
                "Sangre en orina", "Debilidad", "Intolerancia al ejercicio"
            ],
            "pruebas": ["PCR", "Serología (ELISA, IFA)", "Frotis sanguíneo"],
            "prevenciones": ["Control de garrapatas", "Inspección regular", "Uso de antiparasitarios"]
        },
        "Ehrlichia canis": {
            "sintomas": [
                "Fiebre elevada y persistente", "Letargo", "Pérdida de apetito", "Hematomas",
                "Sangrado nasal", "Petequias", "Inflamación de los ganglios linfáticos",
                "Dolor articular y muscular", "Cojera", "Anemia", "Pérdida de peso severa",
                "Dificultad respiratoria", "Problemas neurológicos", "Convulsiones", "Ataxia",
                "Insuficiencia renal", "Depresión", "Esplenomegalia", "Uveítis",
                "Trombocitopenia", "Sangrado anormal"
            ],
            "pruebas": ["ELISA", "IFA", "PCR", "Frotis sanguíneo", "Hemograma completo", "Perfil bioquímico"],
            "prevenciones": [
                "Uso de productos anti-garrapatas", "Inspección frecuente",
                "Eliminación rápida de garrapatas", "Mantenimiento del césped corto",
                "Evitar áreas con alta presencia de garrapatas", "Vacunación (si está disponible)"
            ]
        },
        "Babesia canis": {
            "sintomas": [
                "Anemia hemolítica", "Ictericia", "Fiebre alta", "Orina oscura", "Pérdida de peso",
                "Letargo", "Esplenomegalia", "Coagulopatías", "Insuficiencia renal",
                "Debilidad", "Anorexia", "Hemoglobinuria", "Palidez de mucosas", "Taquicardia",
                "Taquipnea", "Linfadenopatía", "Vómitos", "Diarrea", "Colapso en casos severos"
            ],
            "pruebas": [
                "Frotis sanguíneo", "PCR", "ELISA", "IFA",
                "Hemograma completo", "Perfil bioquímico", "Análisis de orina"
            ],
            "prevenciones": [
                "Control de garrapatas", "Inspección regular",
                "Remoción rápida de garrapatas", "Evitar áreas infestadas",
                "Mantenimiento del entorno limpio", "Uso de repelentes",
                "Vacunación en áreas endémicas (si está disponible)"
            ]
        }
    }

    enfermedades_posibles = []
    sintomas_mascota = set(s.nombre for s in sintomas_seleccionados)
    
    for nombre_enfermedad, info in enfermedades_info.items():
        sintomas_coincidentes = sintomas_mascota.intersection(info["sintomas"])
        if sintomas_coincidentes:
            total_sintomas_enfermedad = len(info["sintomas"])
            porcentaje = (len(sintomas_coincidentes) / total_sintomas_enfermedad) * 100
            enfermedades_posibles.append({
                'nombre': nombre_enfermedad,
                'sintomas_coincidentes': list(sintomas_coincidentes),
                'total_sintomas': len(sintomas_coincidentes),
                'porcentaje': round(porcentaje, 2)
            })

    # Ordenar enfermedades por porcentaje de coincidencia
    enfermedades_posibles.sort(key=lambda x: x['porcentaje'], reverse=True)
    return enfermedades_posibles

def editar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect('mascotas:lista_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'mascotas/editar_mascota.html', {'form': form})

 

def lista_mascotas(request):
    mascotas = Mascota.objects.all()
    return render(request, 'mascotas/lista_mascotas.html', {'mascotas': mascotas})

def eliminar_mascota(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        mascota.delete()
        return redirect('mascotas:lista_mascotas')
    return render(request, 'mascotas/eliminar_mascota.html', {'mascota': mascota})

def guardar_mascotas(request):
    if request.method == 'POST':
        mascota_ids = request.POST.getlist('mascota_ids')
        for mascota_id in mascota_ids:
            mascota = Mascota.objects.get(id=mascota_id)
            mascota.nombre = request.POST.get(f'nombre_{mascota_id}')
            mascota.especie = request.POST.get(f'especie_{mascota_id}')
            mascota.raza = request.POST.get(f'raza_{mascota_id}')
            mascota.fecha_nacimiento = request.POST.get(f'fecha_nacimiento_{mascota_id}')
            mascota.propietario = request.POST.get(f'propietario_{mascota_id}')
            mascota.telefono_propietario = request.POST.get(f'telefono_propietario_{mascota_id}')
            mascota.save()
        
        messages.success(request, f'{len(mascota_ids)} mascota(s) actualizada(s) exitosamente.')
        return redirect('lista_mascotas')
     # Si la acción es "guardar" pero el método no es POST, generamos el CSV
    mascota_ids = request.GET.getlist('mascota_ids')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="mascotas_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nombre', 'Especie', 'Raza', 'Fecha de Nacimiento', 'Propietario', 'Teléfono del Propietario'])
    
    mascotas = Mascota.objects.filter(id__in=mascota_ids)
    for mascota in mascotas:
        writer.writerow([
            mascota.nombre,
            mascota.especie,
            mascota.raza,
            mascota.fecha_nacimiento,
            mascota.propietario,
            mascota.telefono_propietario
        ])
    
    return response

def lista_enfermedades(request):
    enfermedades = Enfermedad.objects.all()
    return render(request, 'mascotas/lista_enfermedades.html', {'enfermedades': enfermedades})

def detalle_enfermedad(request, enfermedad_id):
    enfermedad = get_object_or_404(Enfermedad, id=enfermedad_id)
    sintomas = enfermedad.sintomas.all()
    prevenciones = enfermedad.prevenciones.all()
    pruebas_diagnosticas = enfermedad.pruebas_diagnosticas.all()

    # Definir los síntomas comunes
    sintomas_comunes = {
        "todas": ["Fiebre", "Letargo", "Anemia", "Pérdida de peso"],
        "Anaplasma platys y Ehrlichia canis": ["Fiebre", "Letargo", "Anemia", "Pérdida de apetito", "Cojera", "Dolor articular", "Petequias", "Aumento del tamaño de los ganglios linfáticos"],
        "Anaplasma platys y Babesia canis": ["Fiebre", "Anemia", "Letargo", "Pérdida de peso", "Coagulopatías", "Insuficiencia renal"],
        "Ehrlichia canis y Babesia canis": ["Fiebre", "Letargo", "Anemia", "Pérdida de peso", "Problemas neurológicos"]
    }
    
    # Identificar los síntomas comunes para esta enfermedad
    sintomas_comunes_enfermedad = set(sintomas_comunes["todas"])
    for categoria, sintomas_lista in sintomas_comunes.items():
        if enfermedad.nombre in categoria:
            sintomas_comunes_enfermedad.update(sintomas_lista)
    
    # Marcar los síntomas como comunes o no
    sintomas_marcados = []
    for sintoma in sintomas:
        sintomas_marcados.append({
            'nombre': sintoma.nombre,
            'es_comun': sintoma.nombre in sintomas_comunes_enfermedad
        })

    context = {
        'enfermedad': enfermedad,
        'sintomas': sintomas_marcados,
        'sintomas_comunes': list(sintomas_comunes_enfermedad),
        'prevenciones': prevenciones,
        'pruebas_diagnosticas': pruebas_diagnosticas,
    }
    return render(request, 'mascotas/detalle_enfermedad.html', context)

from .models import ExamenMascota
from .forms import ExamenMascotaForm

from django.core.files.storage import default_storage

from django.shortcuts import render, get_list_or_404, redirect

def cargar_examen(request, mascota_nombre):
    mascotas = get_list_or_404(Mascota, nombre=mascota_nombre)
    
    if len(mascotas) > 1:
        # Si hay múltiples mascotas con el mismo nombre, mostramos una lista para elegir
        return render(request, 'mascotas/seleccionar_mascota.html', {'mascotas': mascotas})
    
    mascota = mascotas[0]  # Si solo hay una mascota, la usamos directamente
    
    if request.method == 'POST':
        form = ExamenMascotaForm(request.POST, request.FILES)
        if form.is_valid():
            examen = form.save(commit=False)
            examen.mascota = mascota
            examen.save()
            return redirect('mascotas:detalle_mascota', mascota_nombre=mascota.nombre)
    else:
        form = ExamenMascotaForm()
    
    examenes = ExamenMascota.objects.filter(mascota=mascota)
    return render(request, 'mascotas/cargar_examen.html', {
        'form': form,
        'mascota': mascota,
        'examenes': examenes
    })

def seleccionar_mascota(request):
    mascotas = Mascota.objects.all()
    return render(request, 'seleccionar_mascota.html', {'mascotas': mascotas})

def preparar_detalles_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    sintomas = Sintoma.objects.filter(mascota=mascota)
    examenes = ExamenMascota.objects.filter(mascota=mascota)
    
    # Guardar datos en la sesión
    request.session['mascota_id'] = mascota_id
    request.session['sintomas'] = list(sintomas.values())
    request.session['examenes'] = list(examenes.values())
    
    return render(request, 'confirmar_detalles.html', {
        'mascota': mascota,
        'sintomas': sintomas,
        'examenes': examenes
    })

import PyPDF2
 

from django.shortcuts import render, get_object_or_404, redirect
from django.core.exceptions import MultipleObjectsReturned
from .models import Mascota

def detalle_mascota(request, mascota_nombre):
    try:
        mascota = Mascota.objects.get(nombre=mascota_nombre)
        sintomas = mascota.sintomas.all()
        examenes = mascota.examenes.all()
        examen = mascota.examenes.order_by('-fecha_subida').first()

        if request.method == 'POST' and 'analizar_examen' in request.POST:
            return analizar_examen(request, mascota.id)

        return render(request, 'mascotas/detalle_mascota.html', {
            'mascota': mascota,
            'sintomas': sintomas,
            'examenes': examenes,
            'examen': examen,
        })
    except MultipleObjectsReturned:
        # Si hay múltiples mascotas con el mismo nombre, muestra una lista
        mascotas = Mascota.objects.filter(nombre=mascota_nombre)
        return render(request, 'mascotas/lista_mascotas_mismo_nombre.html', {
            'mascotas': mascotas,
            'nombre': mascota_nombre
        })
    except Mascota.DoesNotExist:
        # Si no se encuentra ninguna mascota con ese nombre
        return render(request, 'mascotas/mascota_no_encontrada.html', {'nombre': mascota_nombre})


#####################################################################################
import PyPDF2
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Mascota
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Asegúrate de descargar los recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('stopwords')
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Mascota
import PyPDF2
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
 
def analizar_examen(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    return _procesar_examen(request, mascota)

def analizar_examen_por_nombre(request, mascota_nombre):
    mascota = get_object_or_404(Mascota, nombre=mascota_nombre)
    return _procesar_examen(request, mascota)


import pdfplumber

def leer_pdf(archivo_pdf):
    texto = ""
    
    try:
        # Abre el archivo PDF
        with pdfplumber.open(archivo_pdf) as pdf:
            # Iterar sobre todas las páginas del PDF
            for pagina in pdf.pages:
                # Extraer el texto de cada página
                texto_pagina = pagina.extract_text()
                
                # Comprobar si hay tablas, y extraer si es necesario
                tablas = pagina.extract_tables()
                if tablas:
                    for tabla in tablas:
                        for fila in tabla:
                            texto_pagina += " | ".join(fila) + "\n"
                
                # Concatenar el texto de todas las páginas
                texto += texto_pagina + "\n"
        
        # Retorna el texto extraído
        return texto
    
    except Exception as e:
        raise ValueError(f"Error al leer el archivo PDF: {str(e)}")



def _procesar_examen(request, mascota):
    examen = mascota.examenes.order_by('-fecha_subida').first()

    if not examen or not examen.archivo_pdf:
        messages.error(request, "No hay examen subido para esta mascota.")
        return redirect('mascotas:detalle_mascota', mascota_nombre=mascota.nombre)

    try:
        # Leer el PDF del examen
        resultados_examen = leer_pdf(examen.archivo_pdf)

        # Generar resumen
        parser = PlaintextParser.from_string(resultados_examen, Tokenizer("spanish"))
        stemmer = Stemmer("spanish")
        summarizer = LsaSummarizer(stemmer)
        summarizer.stop_words = get_stop_words("spanish")
        
        summary = summarizer(parser.document, 3)  # Genera un resumen de 3 oraciones
        
        resumen_examen = "Resumen del examen:\n\n"
        palabras_contadas = 0
        for sentence in summary:
            palabras = str(sentence).split()
            for palabra in palabras:
                resumen_examen += palabra + " "
                palabras_contadas += 1
                if palabras_contadas % 6 == 0:
                    resumen_examen += "\n"
        
        # Interpretar el contenido del examen (valores)
        valores_examen = interpretar_examen(resultados_examen)

        # Análisis avanzado con NLP
        analisis_nlp = analizar_con_nlp(resultados_examen)

        # Realizar un análisis subjetivo o interpretación avanzada
        analisis_subjetivo = analizar_subjetivamente(resultados_examen)

        return render(request, 'mascotas/resultado_analisis_examen.html', {
            'mascota': mascota,
            'examen': examen,
            'resumen_examen': resumen_examen,
            'valores_examen': valores_examen,
            'analisis_nlp': analisis_nlp,
            'analisis_subjetivo': analisis_subjetivo
        })
    except Exception as e:
        messages.error(request, f"Error al analizar el examen: {str(e)}")
        return redirect('mascotas:detalle_mascota', mascota_nombre=mascota.nombre)

def analizar_subjetivamente(resultados_examen):
    # Inicia con una respuesta vacía
    analisis = "Análisis del sistema basado en los resultados del examen:\n\n"


       # Heurísticas basadas en los resultados extraídos
    if "anemia" in resultados_examen.lower():
        analisis += "- Parece que la mascota podría tener anemia. Esto podría estar relacionado con una deficiencia nutricional o una enfermedad crónica.\n"
    if "trombocitopenia" in resultados_examen.lower():
        analisis += "- La mascota podría tener un conteo bajo de plaquetas. Esto sugiere la posibilidad de problemas de coagulación o infecciones virales.\n"
    if "trombocitosis" in resultados_examen.lower():
        analisis += "- La mascota podría tener un conteo elevado de plaquetas. Esto podría indicar inflamación, infección o trastornos mieloproliferativos.\n"
    if "leucopenia" in resultados_examen.lower():
        analisis += "- El conteo bajo de glóbulos blancos podría indicar una supresión de la médula ósea o una enfermedad infecciosa grave.\n"
    if "leucocitosis" in resultados_examen.lower():
        analisis += "- El conteo elevado de glóbulos blancos puede sugerir infección, inflamación o una respuesta al estrés.\n"
    if "deshidratacion" in resultados_examen.lower():
        analisis += "- La presencia de deshidratación podría estar relacionada con una pérdida excesiva de líquidos o un problema de absorción.\n"
    if "insuficiencia_renal" in resultados_examen.lower():
        analisis += "- La insuficiencia renal puede estar presente si hay elevación de creatinina o urea en la sangre. Se recomienda evaluar la función renal.\n"
    if "hipoglucemia" in resultados_examen.lower():
        analisis += "- Niveles bajos de glucosa en sangre podrían indicar problemas metabólicos, intoxicación o enfermedades hepáticas.\n"
    if "hiperglucemia" in resultados_examen.lower():
        analisis += "- Niveles altos de glucosa en sangre podrían sugerir diabetes mellitus o estrés.\n"
    if "hipoproteinemia" in resultados_examen.lower():
        analisis += "- Un nivel bajo de proteínas en sangre puede ser indicativo de problemas hepáticos o renales.\n"
    if "hiperproteinemia" in resultados_examen.lower():
        analisis += "- Un nivel elevado de proteínas puede sugerir inflamación crónica o infecciones.\n"
    if "hipocalcemia" in resultados_examen.lower():
        analisis += "- Niveles bajos de calcio pueden estar asociados con enfermedades paratiroideas o problemas nutricionales.\n"
    if "hipercalcemia" in resultados_examen.lower():
        analisis += "- Niveles altos de calcio podrían indicar enfermedades óseas, neoplasias o hiperparatiroidismo.\n"
    if "hipomagnesemia" in resultados_examen.lower():
        analisis += "- La deficiencia de magnesio puede afectar la función neuromuscular y cardíaca.\n"
    if "hipermagnesemia" in resultados_examen.lower():
        analisis += "- Niveles altos de magnesio pueden estar relacionados con enfermedades renales o deshidratación severa.\n"
    if "acidosis" in resultados_examen.lower():
        analisis += "- La acidosis metabólica puede estar relacionada con problemas renales o diabetes mellitus descompensada.\n"
    if "alcalosis" in resultados_examen.lower():
        analisis += "- La alcalosis puede estar asociada con problemas respiratorios o desequilibrios electrolíticos.\n"
    if "hemorragia" in resultados_examen.lower():
        analisis += "- La presencia de sangre en el examen puede indicar hemorragias internas o problemas de coagulación.\n"
    if "ictericia" in resultados_examen.lower():
        analisis += "- La ictericia puede ser un signo de enfermedades hepáticas o problemas de descomposición de glóbulos rojos.\n"
    if "hipotension" in resultados_examen.lower():
        analisis += "- La hipotensión podría ser un signo de shock, deshidratación o problemas cardíacos.\n"
    if "hipertension" in resultados_examen.lower():
        analisis += "- La hipertensión puede estar relacionada con enfermedades renales o problemas endocrinos.\n"
    if "glucosuria" in resultados_examen.lower():
        analisis += "- La presencia de glucosa en la orina puede sugerir diabetes mellitus no controlada.\n"
    if "cetonuria" in resultados_examen.lower():
        analisis += "- La presencia de cetonas en la orina puede ser un indicio de cetosis o diabetes mellitus descompensada.\n"
    if "proteinuria" in resultados_examen.lower():
        analisis += "- La presencia de proteínas en la orina podría indicar enfermedades renales o problemas en el tracto urinario.\n"
    if "hematuria" in resultados_examen.lower():
        analisis += "- La presencia de sangre en la orina puede indicar infecciones urinarias o problemas en el tracto urinario.\n"
    if "bacteriuria" in resultados_examen.lower():
        analisis += "- La presencia de bacterias en la orina puede indicar una infección urinaria.\n"
    if "cristales_en_orina" in resultados_examen.lower():
        analisis += "- La presencia de cristales puede sugerir problemas renales o de vesícula biliar.\n"
    if "pH_urinario_alto" in resultados_examen.lower():
        analisis += "- Un pH urinario elevado puede estar asociado con infecciones urinarias o problemas metabólicos.\n"
    if "pH_urinario_bajo" in resultados_examen.lower():
        analisis += "- Un pH urinario bajo puede indicar acidosis metabólica o dietas inadecuadas.\n"
    if "elevacion_de_lipidos" in resultados_examen.lower():
        analisis += "- Niveles elevados de lípidos en sangre podrían ser indicativos de problemas hepáticos o metabólicos.\n"
    if "disminucion_de_lipidos" in resultados_examen.lower():
        analisis += "- Niveles bajos de lípidos pueden sugerir problemas de absorción o desnutrición.\n"
    if "elevacion_de_enzimas_hepaticas" in resultados_examen.lower():
        analisis += "- Niveles elevados de enzimas hepáticas pueden estar relacionados con enfermedades del hígado.\n"
    if "baja_de_enzimas_hepaticas" in resultados_examen.lower():
        analisis += "- Niveles bajos de enzimas hepáticas pueden ser indicativos de problemas con la función hepática.\n"
    if "elevacion_de_enzimas_cardiacas" in resultados_examen.lower():
        analisis += "- Niveles elevados de enzimas cardíacas pueden sugerir enfermedades cardíacas o daño miocárdico.\n"
    if "baja_de_enzimas_cardiacas" in resultados_examen.lower():
        analisis += "- Niveles bajos de enzimas cardíacas podrían ser indicativos de problemas cardíacos o desnutrición.\n"
    if "elevacion_de_urea" in resultados_examen.lower():
        analisis += "- Niveles elevados de urea pueden estar asociados con problemas renales o deshidratación.\n"
    if "baja_de_urea" in resultados_examen.lower():
        analisis += "- Niveles bajos de urea pueden indicar problemas hepáticos o desnutrición.\n"
    if "elevacion_de_creatinina" in resultados_examen.lower():
        analisis += "- Niveles elevados de creatinina pueden sugerir insuficiencia renal.\n"
    if "baja_de_creatinina" in resultados_examen.lower():
        analisis += "- Niveles bajos de creatinina pueden estar relacionados con problemas de nutrición o desnutrición.\n"
    if "elevacion_de_colesterol" in resultados_examen.lower():
        analisis += "- Niveles altos de colesterol pueden ser indicativos de enfermedades metabólicas o cardiovasculares.\n"
    if "baja_de_colesterol" in resultados_examen.lower():
        analisis += "- Niveles bajos de colesterol pueden sugerir problemas hepáticos o endocrinos.\n"
    if "elevacion_de_trigliceridos" in resultados_examen.lower():
        analisis += "- Niveles elevados de triglicéridos pueden estar relacionados con diabetes mellitus o enfermedades metabólicas.\n"
    if "baja_de_trigliceridos" in resultados_examen.lower():
        analisis += "- Niveles bajos de triglicéridos pueden indicar problemas de absorción o desnutrición.\n"
    if "elevacion_de_sodio" in resultados_examen.lower():
        analisis += "- Niveles elevados de sodio pueden ser indicativos de deshidratación o problemas endocrinos.\n"
    if "baja_de_sodio" in resultados_examen.lower():
        analisis += "- Niveles bajos de sodio pueden estar relacionados con problemas renales o enfermedades metabólicas.\n"
    if "elevacion_de_potasio" in resultados_examen.lower():
        analisis += "- Niveles elevados de potasio pueden sugerir problemas renales o desequilibrio electrolítico.\n"
    if "baja_de_potasio" in resultados_examen.lower():
        analisis += "- Niveles bajos de potasio pueden indicar deshidratación o problemas endocrinos.\n"
    if "edema" in resultados_examen.lower():
        analisis += "- La presencia de edema podría estar relacionada con problemas cardíacos, renales o hepáticos.\n"
    if "dificultad_respiratoria" in resultados_examen.lower():
        analisis += "- La dificultad para respirar puede indicar enfermedades respiratorias o cardíacas.\n"
    if "cambios_en_peso" in resultados_examen.lower():
        analisis += "- Los cambios significativos en el peso pueden estar relacionados con problemas metabólicos, endocrinos o nutricionales.\n"
    if "cambios_en_apetito" in resultados_examen.lower():
        analisis += "- Los cambios en el apetito pueden ser indicativos de problemas digestivos, endocrinos o metabólicos.\n"
    if "alteraciones_en_ritmo_cardiaco" in resultados_examen.lower():
        analisis += "- Las alteraciones en el ritmo cardíaco podrían sugerir problemas cardíacos o desequilibrios electrolíticos.\n"
    if "dificultad_en_marchar" in resultados_examen.lower():
        analisis += "- La dificultad para marchar puede estar relacionada con problemas neuromusculares o esqueléticos.\n"
    if "erlichiosis" in resultados_examen.lower():
        analisis += "- Se detectan signos de Erlichiosis. Esta enfermedad, transmitida por garrapatas, puede causar fiebre, anemia y problemas de coagulación.\n"
    if "leishmaniasis" in resultados_examen.lower():
        analisis += "- Los resultados indican una posible infección por Leishmaniasis. Es una enfermedad parasitaria que afecta la piel y órganos internos.\n"
    if "distemper" in resultados_examen.lower() or "moquillo" in resultados_examen.lower():
        analisis += "- Hay indicios de Distemper (Moquillo). Es una enfermedad viral altamente contagiosa que puede afectar los sistemas respiratorio, digestivo y nervioso.\n"
    if "parvovirus" in resultados_examen.lower():
        analisis += "- Los síntomas sugieren infección por Parvovirus. Es una enfermedad viral grave que afecta principalmente el tracto gastrointestinal de los cachorros.\n"
    if "filariasis" in resultados_examen.lower() or "gusano del corazón" in resultados_examen.lower():
        analisis += "- Se detectan signos de Filariasis (Gusano del corazón). Esta enfermedad parasitaria puede afectar gravemente el corazón y los pulmones.\n"
    if "leptospirosis" in resultados_examen.lower():
        analisis += "- Los resultados sugieren una posible infección por Leptospirosis, una enfermedad bacteriana que afecta los riñones y el hígado.\n"
    if "giardia" in resultados_examen.lower():
        analisis += "- La presencia de Giardia sugiere una infección intestinal por parásitos, causando diarrea y pérdida de peso.\n"
    if "babesia" in resultados_examen.lower():
        analisis += "- Los resultados indican Babesiosis, una enfermedad transmitida por garrapatas que destruye los glóbulos rojos y causa anemia.\n"
    if "anaplasmosis" in resultados_examen.lower():
        analisis += "- La mascota muestra signos de Anaplasmosis, una infección transmitida por garrapatas que puede causar fiebre, letargo y pérdida de apetito.\n"
    if "dirofilaria" in resultados_examen.lower():
        analisis += "- La presencia de Dirofilaria sugiere una posible infección por gusanos del corazón, que afecta el sistema cardiovascular.\n"
    if "dermatitis" in resultados_examen.lower():
        analisis += "- Los síntomas indican la posibilidad de Dermatitis, una inflamación de la piel que puede ser causada por alergias o infecciones.\n"
    if "gastritis" in resultados_examen.lower():
        analisis += "- La mascota podría estar sufriendo de Gastritis, una inflamación del estómago que puede causar vómitos y malestar abdominal.\n"
    if "enteritis" in resultados_examen.lower():
        analisis += "- Los resultados sugieren Enteritis, una inflamación del intestino que provoca diarrea y deshidratación.\n"
    if "piroplasmosis" in resultados_examen.lower():
        analisis += "- Los signos sugieren una posible infección por Piroplasmosis, una enfermedad transmitida por garrapatas que destruye los glóbulos rojos.\n"
    if "hepatitis" in resultados_examen.lower():
        analisis += "- Se detectan indicios de Hepatitis infecciosa canina, una enfermedad viral que afecta el hígado.\n"
    if "tos de las perreras" in resultados_examen.lower():
        analisis += "- Los síntomas indican Tos de las Perreras, una enfermedad respiratoria contagiosa que provoca tos seca y persistente.\n"
    if "coronavirus" in resultados_examen.lower():
        analisis += "- Se detectan signos de infección por Coronavirus canino, que puede causar diarrea en cachorros jóvenes.\n"
    if "insuficiencia renal" in resultados_examen.lower():
        analisis += "- Los resultados indican insuficiencia renal, lo que podría estar afectando la capacidad de los riñones para filtrar correctamente.\n"
    if "obesidad" in resultados_examen.lower():
        analisis += "- La mascota muestra signos de obesidad. Se recomienda un control de la dieta y aumento en la actividad física.\n"
    if "hipertensión" in resultados_examen.lower():
        analisis += "- Los resultados sugieren hipertensión, lo que podría estar afectando la presión arterial y los vasos sanguíneos.\n"
    if "anemia" in resultados_examen.lower():
        analisis += "- Parece que la mascota podría tener anemia. Esto podría estar relacionado con una deficiencia nutricional o una enfermedad crónica.\n"
    if "trombocitopenia" in resultados_examen.lower():
        analisis += "- La mascota podría tener un conteo bajo de plaquetas. Esto sugiere la posibilidad de problemas de coagulación o infecciones virales.\n"
    if "normal" in resultados_examen.lower():
        analisis += "- Los resultados parecen estar dentro de los rangos normales. Esto sugiere que la mascota está en buen estado de salud.\n"
    if "leishmaniasis" in resultados_examen.lower():
        analisis += "- Podría haber indicios de leishmaniasis, una enfermedad parasitaria transmitida por mosquitos. Se recomienda realizar pruebas adicionales.\n"
    if "ehrlichiosis" in resultados_examen.lower():
        analisis += "- Los resultados sugieren ehrlichiosis, una infección bacteriana comúnmente transmitida por garrapatas.\n"
    if "parvovirus" in resultados_examen.lower():
        analisis += "- Hay signos de parvovirus canino, una enfermedad viral altamente contagiosa que afecta el sistema digestivo de los perros.\n"
    if "distemper" in resultados_examen.lower():
        analisis += "- La mascota podría tener moquillo canino (distemper), una enfermedad viral que afecta el sistema respiratorio, digestivo y nervioso.\n"
    if "dirofilaria" in resultados_examen.lower():
        analisis += "- Se han detectado indicios de infección por dirofilaria (gusano del corazón), una enfermedad transmitida por mosquitos.\n"
    if "giardiasis" in resultados_examen.lower():
        analisis += "- Los resultados podrían indicar giardiasis, una infección intestinal causada por un parásito.\n"
    if "anaplasmosis" in resultados_examen.lower():
        analisis += "- La mascota podría estar afectada por anaplasmosis, una enfermedad transmitida por garrapatas que afecta a los glóbulos blancos.\n"
    if "babesiosis" in resultados_examen.lower():
        analisis += "- Los resultados sugieren la posibilidad de babesiosis, una infección transmitida por garrapatas que afecta a los glóbulos rojos.\n"
    if "insuficiencia renal" in resultados_examen.lower():
        analisis += "- La mascota podría tener insuficiencia renal, con niveles elevados de urea o creatinina que sugieren problemas en la función renal.\n"
    if "hipoglucemia" in resultados_examen.lower():
        analisis += "- Los niveles bajos de glucosa indican hipoglucemia, lo cual podría ser consecuencia de problemas metabólicos o desnutrición.\n"
    if "hiperglucemia" in resultados_examen.lower():
        analisis += "- Los niveles elevados de glucosa en sangre podrían ser un signo de diabetes mellitus o estrés severo.\n"
    if "insuficiencia hepática" in resultados_examen.lower():
        analisis += "- Los resultados sugieren insuficiencia hepática, lo cual podría estar relacionado con una enfermedad hepática avanzada.\n"
    if "displasia de cadera" in resultados_examen.lower():
        analisis += "- Se han detectado signos de displasia de cadera, una condición común que afecta la movilidad en perros de razas grandes.\n"
    if "gastritis" in resultados_examen.lower():
        analisis += "- La mascota podría tener gastritis, una inflamación del revestimiento del estómago, que podría estar causando vómitos o malestar.\n"
    if "colitis" in resultados_examen.lower():
        analisis += "- Los signos podrían estar relacionados con colitis, una inflamación del colon que provoca diarrea y dolor abdominal.\n"
    if "otitis" in resultados_examen.lower():
        analisis += "- La presencia de otitis, una infección del oído, es posible. Se recomienda revisar los oídos de la mascota para confirmar.\n"
    if "dermatitis" in resultados_examen.lower():
        analisis += "- Los síntomas podrían estar relacionados con dermatitis, una inflamación de la piel que puede ser causada por alergias o infecciones.\n"
    if "enteritis" in resultados_examen.lower():
        analisis += "- La mascota muestra signos de enteritis, una inflamación del intestino que puede causar diarrea severa.\n"
    if "pancreatitis" in resultados_examen.lower():
        analisis += "- Los resultados sugieren pancreatitis, una inflamación del páncreas que puede causar vómitos, dolor abdominal y letargo.\n"   
    if "toxoplasmosis" in resultados_examen.lower():
        analisis += "- Se han encontrado indicios de toxoplasmosis, una infección parasitaria que puede afectar varios órganos.\n"
    if "problema cardíaco" in resultados_examen.lower():
        analisis += "- Se podrían estar detectando signos de una enfermedad cardíaca. Se recomienda una ecocardiografía o análisis cardíacos adicionales.\n"
    if "obesidad" in resultados_examen.lower():
        analisis += "- Los resultados sugieren que la mascota podría tener obesidad, lo cual aumenta el riesgo de enfermedades cardíacas y articulares.\n"
    if "deshidratación" in resultados_examen.lower():
        analisis += "- Hay signos de deshidratación en la mascota. Se recomienda administrar líquidos y monitorear el estado general.\n"
    if "piómetra" in resultados_examen.lower():
        analisis += "- Podría haber indicios de piómetra, una infección uterina grave que requiere atención médica inmediata.\n"
    if "diarrea" in  resultados_examen.lower():
        analisis += "- La mascota podría estar sufriendo de diarrea, lo cual podría estar asociado a infecciones, parásitos o intolerancias alimentarias.\n"

    
    
     # Si todos los valores están en el rango normal
    if not analisis.strip():
         analisis = "Los resultados parecen estar dentro de los rangos normales. Esto sugiere que la mascota está en buen estado de salud."
    else:
        analisis = "Analisis de enfermades subjetivas dio negativo. Se espera el recuento de valores en la seccion de abajo."

    return analisis


def leer_pdf(archivo_pdf):
    texto_examen = ""
    try:
        with archivo_pdf.open('rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                texto_examen += page.extract_text() + "\n\n"
        texto_examen = limpiar_texto(texto_examen)
    except Exception as e:
        print(f"Error al procesar el PDF: {str(e)}")
    return texto_examen

def limpiar_texto(texto):
    texto = ''.join(char for char in texto if char.isprintable() or char in ['\n', '\t'])
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'\n\s*\n', '\n\n', texto)
    return texto.strip()

############################

def interpretar_examen(texto_examen):
# Usar sumy para generar un resumen
   
    # Usar sumy para generar un resumen
    parser = PlaintextParser.from_string(texto_examen, Tokenizer("spanish"))
    stemmer = Stemmer("spanish")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("spanish")
    
    # Generar un resumen de aproximadamente 50 palabras
    summary = summarizer(parser.document, 50)  # Ajusta este número según sea necesario
    
    # Crear un resumen del examen
    interpretacion = ""
    for sentence in summary:
        words = str(sentence).split()
        for i, word in enumerate(words):
            interpretacion += word + " "
            if (i + 1) % 12 == 0:   
                interpretacion += "\n"
        interpretacion += "\n"  # Salto de línea adicional entre oraciones
    
    # Análisis adicional basado en parámetros clave
    interpretacion += ""
    
    # Lista de parámetros a buscar con sus rangos normales
    parametros = [
         
    ]
    
    anomalias = []
    for parametro, min_valor, max_valor, unidad in parametros:
        valor = extraer_valor(texto_examen, parametro)
        if valor != "No encontrado":
            try:
                valor_float = float(valor)
                interpretacion += f"- {parametro.capitalize()}: {valor_float} {unidad}\n"
                if valor_float < min_valor:
                    interpretacion += f"  El nivel de {parametro} está por debajo del rango normal ({min_valor}-{max_valor} {unidad}). "
                    anomalias.append(f"nivel bajo de {parametro}")
                elif valor_float > max_valor:
                    interpretacion += f"  El nivel de {parametro} está por encima del rango normal ({min_valor}-{max_valor} {unidad}). "
                    anomalias.append(f"nivel alto de {parametro}")
                else:
                    interpretacion += f"  El nivel de {parametro} está dentro del rango normal ({min_valor}-{max_valor} {unidad}). "
                interpretacion += "\n"
            except ValueError:
                interpretacion += f"- {parametro.capitalize()}: No se pudo interpretar el valor '{valor}'\n"
        else:
            interpretacion += f"- {parametro.capitalize()}: No se encontró información\n"
    
    # Generar diagnóstico sugerido
    diagnostico = ""
    if "nivel bajo de plaquetas" in anomalias:
        diagnostico += "- El bajo recuento de plaquetas sugiere la presencia de infecciones por proteobacterias de la familia Anaplasmataceae, "
        diagnostico += "que incluye géneros como Ehrlichia, Anaplasma y Neorickettsia. "
        diagnostico += "Se observan macroplaquetas y un recuento de plaquetas por debajo del rango normal. "
    if "nivel bajo de hemoglobina" in anomalias or "nivel bajo de eritrocitos" in anomalias:
        diagnostico += "- Se detecta una posible anemia. Esto puede ser causado por pérdida de sangre, destrucción de glóbulos rojos o producción insuficiente de glóbulos rojos. "
    if "nivel alto de leucocitos" in anomalias:
        diagnostico += "- El alto recuento de leucocitos sugiere una posible infección, inflamación o respuesta inmunitaria activa. "
    if "nivel alto de glucosa" in anomalias:
        diagnostico += "- La elevación de glucosa puede indicar diabetes mellitus o estrés. "
    if "nivel alto de creatinina" in anomalias or "nivel alto de urea" in anomalias:
        diagnostico += "- Los niveles elevados de creatinina y/o urea sugieren una posible insuficiencia renal. "
    if "nivel alto de alt" in anomalias or "nivel alto de ast" in anomalias:
        diagnostico += "- La elevación de enzimas hepáticas (ALT, AST) indica posible daño hepático. "
    if "nivel alto de fosfatasa alcalina" in anomalias:
        diagnostico += "- El aumento de fosfatasa alcalina puede sugerir problemas hepáticos, óseos o endocrinos. "
    if "nivel bajo de albúmina" in anomalias:
        diagnostico += "- La disminución de albúmina puede indicar problemas hepáticos, renales o malnutrición. "
    
    if not anomalias:
        diagnostico += " "
    
    diagnostico += ""
    
    interpretacion += diagnostico
    interpretacion += ""
    
    return interpretacion

def extraer_valor(texto, parametro):
    import re
    patron = rf"{parametro}[:\s]+(\d+(?:\.\d+)?)"
    match = re.search(patron, texto, re.IGNORECASE)
    if match:
        return match.group(1)
    return "No encontrado"
 


def analizar_con_nlp(texto_examen):
    # Tokenización y eliminación de stopwords
    tokens = word_tokenize(texto_examen.lower())
    stop_words = set(stopwords.words('spanish'))
    filtered_tokens = [w for w in tokens if w not in stop_words and w.isalnum()]
    
    # Análisis de frecuencia de palabras
    freq_dist = FreqDist(filtered_tokens)
    palabras_comunes = freq_dist.most_common(10)
    
    # Contar oraciones
    oraciones = sent_tokenize(texto_examen)
    
    return {
        'palabras_comunes': palabras_comunes,
        'total_palabras': len(tokens),
        'palabras_unicas': len(set(tokens)),
        'total_oraciones': len(oraciones),
        'longitud_promedio_oracion': sum(len(sent.split()) for sent in oraciones) / len(oraciones) if oraciones else 0
    }

########################################################################

from django.shortcuts import render, redirect
from .models import Sintoma, Tratamiento
from django.contrib import messages
from django.utils import timezone

def experto(request):
    if request.method == 'POST':
        if 'sintoma' in request.POST:
            nuevo_sintoma = request.POST.get('sintoma')
            Sintoma.objects.create(nombre=nuevo_sintoma)
            messages.success(request, f'Síntoma "{nuevo_sintoma}" añadido correctamente.')
        elif 'tratamiento' in request.POST:
            nuevo_tratamiento = request.POST.get('tratamiento')
            enfermedad_id = request.POST.get('enfermedad_id')
            mascota_id = request.POST.get('mascota_id')  # Asegúrate de tener este campo en el formulario
            if enfermedad_id and mascota_id:
                enfermedad = Enfermedad.objects.get(id=enfermedad_id)
                mascota = Mascota.objects.get(id=mascota_id)
                Tratamiento.objects.create(
                    descripcion=nuevo_tratamiento,
                    enfermedad=enfermedad,
                    mascota=mascota,
                    fecha_inicio=timezone.now().date()
                )
                messages.success(request, f'Tratamiento añadido correctamente para {mascota.nombre}.')
            else:
                messages.success(request, f'Tratamiento añadido correctamente para {mascota.nombre}.')
                return redirect('mascotas:lista_tratamientos')

    sintomas = Sintoma.objects.all()
    tratamientos = Tratamiento.objects.all()
    enfermedades = Enfermedad.objects.all()
    mascotas = Mascota.objects.all()  # Asegúrate de obtener todas las mascotas
    context = {
        'sintomas': sintomas,
        'tratamientos': tratamientos,
        'enfermedades': enfermedades,
        'mascotas': mascotas,  # Añade las mascotas al contexto
    }
    return render(request, 'mascotas/experto.html', context)

def lista_tratamientos(request):
    tratamientos = Tratamiento.objects.all().order_by('-fecha_inicio')
    return render(request, 'mascotas/lista_tratamientos.html', {'tratamientos': tratamientos})

def eliminar_sintoma(request, sintoma_id):
    sintoma = get_object_or_404(Sintoma, id=sintoma_id)
    sintoma.delete()
    messages.success(request, f'Síntoma "{sintoma.nombre}" eliminado correctamente.')
    return redirect('mascotas:experto')

def eliminar_tratamiento(request, tratamiento_id):
    tratamiento = get_object_or_404(Tratamiento, id=tratamiento_id)
    tratamiento.delete()
    messages.success(request, 'Tratamiento eliminado correctamente.')
    return redirect('mascotas:lista_tratamientos')  # Cambiado para redirigir a la lista de tratamientos



def entrenar_modelo(request):
 modelo = ModeloIA()
 mascotas = Mascota.objects.all()

 X = []
 y = []
    
 for mascota in mascotas:
        sintomas = [sintoma.id for sintoma in mascota.sintomas.all()]
        enfermedades = [enfermedad.id for enfermedad in mascota.enfermedades.all()]
        
        if sintomas and enfermedades:
            X.append(sintomas)
            y.append(enfermedades[0])  # Asumimos una enfermedad por mascota
    
 if X and y:
        modelo.entrenar(X, y)
        messages.success(request, "Modelo de IA entrenado exitosamente.")
 else:
        messages.warning(request, "No hay suficientes datos para entrenar el modelo.")
    
        return redirect('mascotas:lista_mascotas')
 return redirect('mascotas:experto')