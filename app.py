from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def convert_to_webp(input_path, output_path):
    with Image.open(input_path) as img:
        img.save(output_path, 'webp')

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            output_path = os.path.splitext(input_path)[0] + '.webp'
            file.save(input_path)
            convert_to_webp(input_path, output_path)
            return send_from_directory(app.config['UPLOAD_FOLDER'], output_path.split('/')[-1], as_attachment=True)

    return render_template('upload.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
