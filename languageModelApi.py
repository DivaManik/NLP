from flask import Flask, request, jsonify
from languageModel import baca_pdf_fitz, build_ngram_index, predict_kata
from flask_cors import CORS  
import os

app = Flask(__name__)
CORS(app)


folder = './dokumen'
documents = []

for filename in os.listdir(folder):
    if filename.endswith('.pdf'):
        try:
            filepath = os.path.join(folder, filename)
            text = baca_pdf_fitz(filepath)
            documents.append(text)
        except Exception as e:
            print(f"Gagal membaca {filename}: {e}")


unigrams, bigrams, trigrams = build_ngram_index(documents)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({'error': 'Parameter "query" dibutuhkan'}), 400
    
    query = data['query']
    result = predict_kata(query, unigrams, bigrams, trigrams)
    return jsonify({
        'predict': result
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
