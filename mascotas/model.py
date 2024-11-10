# mascotas/model.py
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.naive_bayes import GaussianNB
from .models import Mascota, Sintoma, Enfermedad

class ModeloIA:
    def __init__(self):
        self.model = GaussianNB()
        self.le_sintomas = LabelEncoder()
        self.le_enfermedades = LabelEncoder()
        self.n_features = None

    def entrenar(self):
        mascotas = Mascota.objects.all().prefetch_related('sintomas', 'enfermedades')
        
        X = []
        y = []
        
        for mascota in mascotas:
            sintomas = [sintoma.nombre for sintoma in mascota.sintomas.all()]
            enfermedades = [enfermedad.nombre for enfermedad in mascota.enfermedades.all()]
            
            if sintomas and enfermedades:
                X.append(sintomas)
                y.append(enfermedades[0])  # Asumimos una enfermedad por mascota
        
        if not X or not y:
            raise ValueError("No hay suficientes datos para entrenar el modelo.")
        
        # Codificar síntomas y enfermedades
        self.le_sintomas.fit(Sintoma.objects.values_list('nombre', flat=True))
        self.le_enfermedades.fit(Enfermedad.objects.values_list('nombre', flat=True))
        
        # Convertir síntomas a formato one-hot
        X_encoded = np.zeros((len(X), len(self.le_sintomas.classes_)))
        for i, sintomas_mascota in enumerate(X):
            indices = self.le_sintomas.transform(sintomas_mascota)
            X_encoded[i, indices] = 1
        
        y_encoded = self.le_enfermedades.transform(y)
        
        self.n_features = X_encoded.shape[1]
        self.model.fit(X_encoded, y_encoded)

    def predecir(self, sintomas):
        if not self.esta_entrenado():
            raise ValueError("El modelo no ha sido entrenado aún.")
        
        sintomas_array = np.zeros(self.n_features)
        indices = self.le_sintomas.transform(sintomas)
        sintomas_array[indices] = 1
        
        prediccion_encoded = self.model.predict([sintomas_array])
        return self.le_enfermedades.inverse_transform(prediccion_encoded)
    
    def esta_entrenado(self):
        return self.n_features is not None

def entrenar():
    modelo = ModeloIA()
    try:
        modelo.entrenar()
        return modelo
    except ValueError as e:
        print(f"Error al entrenar el modelo: {str(e)}")
        return None