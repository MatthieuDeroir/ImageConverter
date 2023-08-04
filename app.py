from flask import Flask, render_template, request, send_from_directory, send_file
from PIL import Image
import zipfile
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
        files = request.files.getlist('file')
        if files:
            # Create a ZIP file to hold the converted images
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_images.zip')
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in files:
                    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    output_path = os.path.splitext(input_path)[0] + '.webp'
                    file.save(input_path)
                    convert_to_webp(input_path, output_path)
                    # Add the converted file to the ZIP
                    zipf.write(output_path, os.path.basename(output_path))
            return send_file(zip_path, as_attachment=True, download_name='converted_images.zip')

    return render_template('upload.html')


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
