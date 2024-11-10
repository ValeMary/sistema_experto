from django.apps import AppConfig
import nltk 

class MiAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mi_app'

    def ready(self):
        # Verifica si los recursos de NLTK ya están descargados
        try:
            nltk.download('punkt_tab')
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
