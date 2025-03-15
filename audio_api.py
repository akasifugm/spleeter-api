from flask import Flask, request, jsonify, send_from_directory
import os
from spleeter.separator import Separator

# Initialize Flask App
app = Flask(__name__)

# Define output directory
OUTPUT_DIR = "C:/spleeter/output"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def home():
    return "Flask server is running! Use /separate to process audio."

# Route to process audio separation with different model options
@app.route('/separate', methods=['POST'])
def separate_audio():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Get stem type from request (default to 5stems)
    stem_option = request.form.get("stems", "5stems")
    valid_models = {"2stems", "4stems", "5stems"}
    
    if stem_option not in valid_models:
        return jsonify({"error": "Invalid stem option. Choose from 2stems, 4stems, or 5stems"}), 400

    # Save uploaded file
    input_path = os.path.join(OUTPUT_DIR, file.filename)
    file.save(input_path)

    # Separate audio using selected model
    separator = Separator(f'spleeter:{stem_option}')
    separator.separate_to_file(input_path, OUTPUT_DIR)

    # Define output paths
    filename = os.path.splitext(file.filename)[0]
    output_folder = os.path.join(OUTPUT_DIR, filename)
    
    stems_files = os.listdir(output_folder)
    stems_dict = {stem.split(".")[0]: f"/download/{filename}/{stem}" for stem in stems_files}

    return jsonify({
        "message": f"Separation successful using {stem_option}!",
        **stems_dict
    })

# Route to download separated files
@app.route('/download/<folder>/<stem>', methods=['GET'])
def download_file(folder, stem):
    folder_path = os.path.join(OUTPUT_DIR, folder)
    file_path = os.path.join(folder_path, stem)

    if os.path.exists(file_path):
        return send_from_directory(folder_path, stem, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

# Run the Flask App
if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()  # Prevent Windows multiprocessing issues
    app.run(debug=True, host='0.0.0.0', port=5000)
