import os
import re
import csv
import fitz  
import nltk
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from collections import Counter

nltk.download('punkt')

folder = './dokumen'  

def baca_pdf_fitz(file_path):
    doc = fitz.open(file_path)
    text = ''
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = word_tokenize(text)
    return tokens

def save_to_CSV(counter, filename):
    f = open(filename, 'w', encoding='utf-8')
    f.write('ngram,frequency\n')
    
    for ngram, freq in counter.items():
        if isinstance(ngram, tuple):
            ngram_text = ''
            for i, word in enumerate(ngram):
                if i == 0:
                    ngram_text = word
                else:
                    ngram_text = ngram_text + ' ' + word
        else:
            ngram_text = ngram
        line = ngram_text + ',' + str(freq) + '\n'
        f.write(line)
    f.close()

def build_ngram_index(documents):
    unigrams = Counter()
    bigrams = Counter()
    trigrams = Counter()
    for doc in documents:
        tokens = preprocess(doc)
        unigrams.update(tokens)
        bigrams.update(ngrams(tokens, 2))
        trigrams.update(ngrams(tokens, 3))
    return unigrams, bigrams, trigrams

def predict_kata(query, unigrams, bigrams, trigrams):
   
    tokens = preprocess(query)
    candidates = {}
    jumlah_kata = len(tokens)
    
    if jumlah_kata == 2:
        kata1 = tokens[0]
        kata2 = tokens[1]
        for trigram, frekuensi in trigrams.items():
            if trigram[0] == kata1 and trigram[1] == kata2:
                kata_ketiga = trigram[2]
                candidates[kata_ketiga] = frekuensi
    elif jumlah_kata == 1:
        kata1 = tokens[0]
        for bigram, frekuensi in bigrams.items():
            if bigram[0] == kata1:
                kata_kedua = bigram[1]
                candidates[kata_kedua] = frekuensi
    else:
        return ["(Maaf Maksimal 2 Kata Untuk Prediksi)"]
    if len(candidates) == 0:
        return ["(Tidak ada prediksi ditemukan)"]

    sorted_list = []
    
    for kata, frekuensi in candidates.items():
        sorted_list.append([frekuensi, kata])
    
    sorted_list.sort(reverse=True)
    
    hasil = []
    count = 0
    for frekuensi, kata in sorted_list:  
        if count < 10:
            hasil.append(kata)
            count = count + 1
        else:
            break
    
    return hasil

def main():

    documents = []
    for filename in os.listdir(folder):
        if filename.endswith('.pdf'):
            filepath = os.path.join(folder, filename)
            try:
                text = baca_pdf_fitz(filepath)
                documents.append(text)
            except Exception as e:
                print(f"Gagal membaca {filename}: {e}")


    unigrams, bigrams, trigrams = build_ngram_index(documents)

    save_to_CSV(unigrams, 'unigram_index.csv')
    save_to_CSV(bigrams, 'bigram_index.csv')
    save_to_CSV(trigrams, 'trigram_index.csv')

    while True:
        query = input("Masukkan 1 kata untuk bigram, 2 kata untuk trigram dan exit untuk keluar : ")
        if query.lower() == 'exit':
            break
        predictions = predict_kata(query, unigrams, bigrams, trigrams)
        print("Kemungkinan kata berikutnya:", predictions)

if __name__ == "__main__":
    main()
