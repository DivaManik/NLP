import os
import string
import nltk
import fitz
import csv
import pickle
import numpy as np

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.corpus import stopwords  
stop_words = set(stopwords.words('indonesian'))

factory = StemmerFactory() 
stemmer = factory.create_stemmer() 


def normalisasi(text):
    text_lower = text.lower()
    return text_lower.translate(str.maketrans('', '', string.punctuation))

def preproses(text):
    norma = normalisasi(text)
    tokenize = nltk.word_tokenize(norma)
    
    filtered = []
    for word in tokenize:
        if word not in stop_words and word.isalpha():
            filtered.append(stemmer.stem(word))
    
    return filtered


def ambil_text_pdf(file_path):
    doc = fitz.open(file_path)
    all_text = ''
    for page in doc:
        all_text += page.get_text()
    return all_text


def proses_dokumen(direktori):
    dokumens, nama_dokumen = [], []
    for filename in sorted(os.listdir(direktori)):
        if filename.endswith('.pdf'):
            file_path = os.path.join(direktori, filename)
            dokumen = ambil_text_pdf(file_path)
            processed = preproses(dokumen)
            dokumens.append(processed)
            nama_dokumen.append(filename)
    return dokumens, nama_dokumen

def gabungkan_dokumen(dokumen):
    hasil = []
    for doc in dokumen:
        gabung = ' '.join(doc)
        hasil.append(gabung)
    return hasil

def hitung_tfidf(dokumen_str):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(dokumen_str)
    fitur = vectorizer.get_feature_names_out()
    return tfidf_matrix, vectorizer, fitur

def simpan_index_csv(tfidf_matrix, nama_dokumen, fitur, nama_file='index_tfidf.csv'):
    tfidf_matrix = tfidf_matrix.toarray()
    with open(nama_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Dokumen'] + list(fitur))
        for i, dok in enumerate(nama_dokumen):
            writer.writerow([dok] + list(tfidf_matrix[i]))

def baca_index_csv(nama_file='index_tfidf.csv'):
    tfidf_matrix, nama_dokumen = [], []
    with open(nama_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        fitur = next(reader)[1:]
        for row in reader:
            nama_dokumen.append(row[0])
            tfidf_matrix.append([float(x) for x in row[1:]])
    return np.array(tfidf_matrix), nama_dokumen, fitur

def cari_dokumen(query, vectorizer, tfidf_matrix, nama_dokumen):
    query_tokens = preproses(query)
    query_str = ' '.join(query_tokens)
    query_vec = vectorizer.transform([query_str])
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    hasil = sorted(zip(nama_dokumen, sim_scores), key=lambda x: x[1], reverse=True)
    return hasil


def main():
    direktori = "./dokumen"
    index_file = "index_tfidf.csv"
    model_file = "tfidf_vectorizer.pkl"

    if os.path.exists(index_file) and os.path.exists(model_file):
        tfidf_matrix, nama_dokumen, _ = baca_index_csv(index_file)
        with open(model_file, 'rb') as f:
            vectorizer = pickle.load(f)
    else:
        dokumens, nama_dokumen = proses_dokumen(direktori)
        dokumen_str = gabungkan_dokumen(dokumens)

        tfidf_matrix, vectorizer, fitur = hitung_tfidf(dokumen_str)
        simpan_index_csv(tfidf_matrix, nama_dokumen, fitur, index_file)

        with open(model_file, 'wb') as f:
            pickle.dump(vectorizer, f)

        tfidf_matrix = tfidf_matrix.toarray()

    query = input("\n Masukkan kata pencarian: ")
    hasil = cari_dokumen(query, vectorizer, tfidf_matrix, nama_dokumen)

    print("\n Hasil Pencarian:")
    print(f"{'Nama Dokumen'.ljust(100)} | Skor Kemiripan")
    print("-" * 120)
    for nama, skor in hasil:
        print(f"{nama.ljust(100)} : {skor:.4f}")

if __name__ == "__main__":
    main()
