from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, CSVLoader
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
import ollama

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to extract text from documents
def extract_text(filepath):
    if filepath.endswith(".pdf"):
        text = ""
        with open(filepath, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text
    elif filepath.endswith(".docx"):
        return Docx2txtLoader(filepath).load()
    elif filepath.endswith(".csv") or filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath) if filepath.endswith(".xlsx") else pd.read_csv(filepath)
        return df.to_string()
    return ""

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    text = extract_text(filepath)
    return jsonify({"message": "File uploaded successfully", "text": text})

@app.route("/query", methods=["POST"])
def query_doc():
    data = request.json
    query_text = data.get("query")
    model_name = data.get("model", "llama2")

    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": query_text}])
    return jsonify({"response": response["message"]})

if __name__ == "__main__":
    app.run(debug=True)
