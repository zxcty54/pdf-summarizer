from flask import Flask, request, jsonify
import pdfplumber
from transformers import pipeline

# Load the free Hugging Face summarizer
summarizer = pipeline("summarization", model="t5-small")

app = Flask(__name__)

@app.route("/")
def home():
    return "PDF Summarizer API is Running!"

@app.route("/summarize", methods=["POST"])
def summarize_pdf():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    
    # Extract text from PDF
    with pdfplumber.open(file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

    text = text[:500]  # Truncate if too long
    summary = summarizer(text, max_length=200, min_length=50, do_sample=False)

    return jsonify({"summary": summary[0]["summary_text"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
