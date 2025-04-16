from flask import Flask, render_template, request, send_file, redirect, url_for
import cv2
import os
import uuid
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        contrast = float(request.form.get('contrast', 1.0))  # ברירת מחדל 1.0
        brightness = int(request.form.get('brightness', 0))  # ברירת מחדל 0
        edge_threshold1 = int(request.form.get('threshold1', 50))  # ברירת מחדל 50
        edge_threshold2 = int(request.form.get('threshold2', 150))  # ברירת מחדל 150

        if file:
            filename = str(uuid.uuid4()) + '.png'
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # עיבוד התמונה
            img = cv2.imread(filepath)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # התאמת ניגודיות ובהירות
            gray = cv2.convertScaleAbs(gray, alpha=contrast, beta=brightness)

            # טשטוש להסרת רעשים
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)

            # גילוי קצוות באמצעות Canny
            edges = cv2.Canny(blurred, edge_threshold1, edge_threshold2)

            # עיבוי קווי המתאר
            kernel = np.ones((3, 3), np.uint8)
            thick_edges = cv2.dilate(edges, kernel, iterations=2)

            # היפוך צבעים (שחור על לבן)
            result = 255 - thick_edges

            # שמירת התוצאה
            result_path = os.path.join(UPLOAD_FOLDER, 'result_' + filename)
            cv2.imwrite(result_path, result)

            return render_template('index.html', result_image=result_path, original_image=filepath, download_link=result_path)

    return render_template('index.html', result_image=None, original_image=None, download_link=None)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
