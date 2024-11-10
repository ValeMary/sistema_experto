import nltk

def download_nltk_resources():
    nltk.download('punkt_tab')
    nltk.download('punkt')
    nltk.download('stopwords')

if __name__ == '__main__':
    download_nltk_resources()