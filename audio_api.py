from flask import Flask, request, jsonify
import os
import logging
import tensorflow as tf  # Ensure TensorFlow is imported
from spleeter.separator import Separator

# Force TensorFlow to run on CPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Initialize Flask App
app = Flask(__name__)

# Enable debugging logs
logging.basicConfig(level=logging.DEBUG)

# Define output directory in /tmp (Render allows writing here)
OUTPUT_DIR = "/tmp/spleeter_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the directory exists

@app.route('/')
def home():
    return jsonify({"message": "Spleeter API is running"}), 200

@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        logging.error("No file uploaded.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = os.path.basename(file.filename)  # Ensure safe filename
    input_path = os.path.join(OUTPUT_DIR, filename)

    try:
        file.save(input_path)  # Save uploaded file
        logging.info(f"File saved: {input_path}")  # Debugging log

        # Ensure Spleeter reads from the correct path
        separator = Separator('spleeter:5stems')
        separator.separate_to_file(input_path, OUTPUT_DIR)

        # Find the processed files (e.g., vocals.mp3, drums.mp3, etc.)
        processed_files = os.listdir(os.path.join(OUTPUT_DIR, filename.split('.')[0]))
        processed_files_urls = [
            f"/download/{filename.split('.')[0]}/{f}" for f in processed_files
        ]

        return jsonify({
            "message": "Audio separated successfully",
            "processed_files": processed_files_urls
        }), 200

    except Exception as e:
        logging.error(f"Error: {str(e)}")  # Print error log
        return jsonify({"error": str(e)}), 500

@app.route('/download/<folder>/<filename>', methods=['GET'])
def download_file(folder, filename):
    """ Allow downloading separated audio files """
    return send_from_directory(os.path.join(OUTPUT_DIR, folder), filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  # Debug mode ON
