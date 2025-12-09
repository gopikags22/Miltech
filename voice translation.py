from flask import Flask, request, jsonify
from googletrans import Translator
from langdetect import detect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

translator = Translator()

@app.route('/detect-translate', methods=['POST'])
def detect_and_translate():
    data = request.get_json()
    text = data.get("text", "")
    target_lang = data.get("target_lang", "hi")  # Default to Hindi if not provided

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Step 1: Detect the language
        detected_language = detect(text)

        # Step 2: Translate the text to the target Indian language
        translated = translator.translate(text, src=detected_language, dest=target_lang)

        return jsonify({
            "detected_language": detected_language,
            "translated_text": translated.text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5000)