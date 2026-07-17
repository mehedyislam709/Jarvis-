from flask import Flask, request, jsonify
from PIL import Image
import pytesseract  # এখানে ইমপোর্টটি ঠিক করা হয়েছে
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Voice authentication function placeholder
def authenticate_voice(audio_file):
    # In real scenario, implement speaker verification here
    return True

@app.route('/process_screen', methods=['POST'])
def process_screen():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        os.remove(file_path)  # Clean up the file after processing
        return jsonify({'text': text}), 200
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)  # এরর আসলেও ফাইল ডিলিট করার সেফটি মেজার
        return jsonify({'error': str(e)}), 500

@app.route('/verify_voice', methods=['POST'])
def verify_voice():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file part'}), 400
        
    audio_file = request.files['audio']
    if authenticate_voice(audio_file):
        return jsonify({'status': 'authenticated'}), 200
    else:
        return jsonify({'status': 'unauthorized'}), 401

@app.route('/control_device', methods=['POST'])
def control_device():
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
        
    device = data.get('device')
    action = data.get('action')
    
    # Communication with smart home device
    print(f"Turning {action} the {device}")
    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':  # বাংলা দাড়ি (।) সরিয়ে কোলন দেওয়া হয়েছে
    app.run(host='0.0.0.0', port=5000)

