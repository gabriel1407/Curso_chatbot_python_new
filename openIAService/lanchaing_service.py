import os
import fitz  # PyMuPDF
import docx
import pytesseract
import speech_recognition as sr
from flask import Flask, request, jsonify
import openai
from werkzeug.utils import secure_filename
from pydub import AudioSegment

app = Flask(__name__)

# Configura la clave de API de OpenAI
OPENAI_API_KEY = 'sk-proj-nLBrLl0UjjTMTXJrnf18T3BlbkFJBqxlVI8sdhfdfVxHaoUI'
openai.api_key = OPENAI_API_KEY

# Configura la ruta para guardar los archivos subidos
UPLOAD_FOLDER = os.path.join('local', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def process_pdf(file_path):
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def process_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def process_image(file_path):
    text = pytesseract.image_to_string(file_path)
    return text

def process_audio(file_path):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_file(file_path)
    audio.export(file_path, format="wav")
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    return text

# Ruta para generar completados
@app.route("/generate_completion", methods=["POST"])
def generate_completion():
    data = request.form
    file = request.files.get("file")
    prompt = data.get("message")

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        if filename.endswith('.pdf'):
            prompt = process_pdf(file_path)
        elif filename.endswith('.docx'):
            prompt = process_docx(file_path)
        elif filename.endswith(('.png', '.jpg', '.jpeg')):
            prompt = process_image(file_path)
        elif filename.endswith(('.wav', '.mp3', '.m4a')):
            prompt = process_audio(file_path)
        else:
            return jsonify({"error": "Unsupported file type"}), 400

    if prompt:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        if response and response.choices:
            completion = response.choices[0].message['content'].strip()
            return jsonify({"completion": completion})

    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8082, debug=True)
