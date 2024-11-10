import os
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import GaussianNB

class EnfermedadPredictor:
    def __init__(self):
        self.vectorizer = CountVectorizer()
        self.clf = MultinomialNB()
        self.model_path = os.path.join(os.path.dirname(__file__), 'modelo_enfermedad.joblib')
        self.vectorizer_path = os.path.join(os.path.dirname(__file__), 'vectorizer.joblib')

    def entrenar(self, sintomas, enfermedades):
        if not sintomas or not enfermedades:
            raise ValueError("No hay datos suficientes para entrenar el modelo")
        X = self.vectorizer.fit_transform(sintomas)
        self.clf.fit(X, enfermedades)
        joblib.dump(self.clf, self.model_path)
        joblib.dump(self.vectorizer, self.vectorizer_path)

    def predecir(self, sintomas):
        if not os.path.exists(self.model_path) or not os.path.exists(self.vectorizer_path):
            raise FileNotFoundError("Modelo no encontrado. Entrena el modelo primero.")
        self.clf = joblib.load(self.model_path)
        self.vectorizer = joblib.load(self.vectorizer_path)
        X = self.vectorizer.transform(sintomas)
        return self.clf.predict(X)