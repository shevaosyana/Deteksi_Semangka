from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np

app = Flask(__name__)

# Konfigurasi folder upload dan batas ukuran file
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max-limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Pastikan folder upload ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Memeriksa apakah file memiliki ekstensi yang valid (png, jpg, jpeg)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_watermelon(image_path):
    """Fungsi untuk mendeteksi semangka berdasarkan warna hijau (kulit) dan merah (daging)."""
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Range warna hijau (kulit semangka)
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    
    # Range warna merah (daging semangka)
    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    
    # Mask untuk warna hijau (kulit semangka)
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    # Mask untuk warna merah (daging semangka)
    red_mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
    
    # Hitung persentase warna hijau dan merah
    total_pixels = img.shape[0] * img.shape[1]
    green_pixels = cv2.countNonZero(green_mask)
    red_pixels = cv2.countNonZero(red_mask)
    
    green_percentage = (green_pixels / total_pixels) * 100
    red_percentage = (red_pixels / total_pixels) * 100
    
    if red_percentage > 30 and green_percentage > 20:
        return {
            'condition': 'Ripe Watermelon',
            'confidence': red_percentage / 100,
            'details': 'Semangka matang dengan daging merah dan kulit hijau terdeteksi.'
        }
    elif green_percentage > 50:
        return {
            'condition': 'Unripe Watermelon',
            'confidence': green_percentage / 100,
            'details': 'Semangka belum matang, hanya terdeteksi kulit hijau.'
        }
    else:
        return {
            'condition': 'No Watermelon Detected',
            'confidence': 0,
            'details': 'Tidak ada semangka yang terdeteksi dalam gambar.'
        }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Menerima file gambar dan menganalisisnya menggunakan fungsi analyze_watermelon."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Analisis gambar menggunakan fungsi analyze_watermelon
        result = analyze_watermelon(file_path)
        
        return jsonify({
            'class': result['condition'],
            'confidence': result['confidence'],
            'details': result['details'],
            'image_path': f'/static/uploads/{filename}'  # Menggunakan URL statik untuk gambar
        })
    else:
        return jsonify({'error': 'Invalid file format. Only PNG, JPG, and JPEG are allowed.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
