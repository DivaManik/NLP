from flask import Flask, request, jsonify
from flask_cors import CORS  
import pickle
import numpy as np
import os
from searchDocument import preproses, cari_dokumen, baca_index_csv 

app = Flask(__name__)
CORS(app)  

index_file = "index_tfidf.csv"
model_file = "tfidf_vectorizer.pkl"

if os.path.exists(index_file) and os.path.exists(model_file):
    tfidf_matrix, nama_dokumen, _ = baca_index_csv(index_file)
    with open(model_file, 'rb') as f:
        vectorizer = pickle.load(f)
else:
    raise FileNotFoundError("File index_tfidf.csv atau tfidf_vectorizer.pkl tidak ditemukan. Jalankan file searchDocument.py")

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if 'query' not in data:
        return jsonify({"error": "Parameter 'query' diperlukan"}), 400

    query = data['query']
    hasil = cari_dokumen(query, vectorizer, tfidf_matrix, nama_dokumen)
    hasil_filtered = []
    for nama, skor in hasil:
        if skor > 0:
            hasil_filtered.append({
                "dokumen": nama,
                "skor": round(skor, 4)
            })

    return jsonify({
        "query": query,
        "results": hasil_filtered
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000)
