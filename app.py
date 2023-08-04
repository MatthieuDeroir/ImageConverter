from flask import Flask, render_template, request, send_file, Response
from PIL import Image
import os
import zipfile
import logging
import shutil



# logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['DEBUG_LOGGING'] = False  # Set to False in production

if app.config['DEBUG_LOGGING']:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
unique_visitors = set()

def convert_image(input_path, output_path, format):
    with Image.open(input_path) as img:
        logging.debug(f'Converting image from {input_path} to {output_path} with format {format}')
        img.save(output_path, format=format)

def clear_upload_folder():
    folder = app.config['UPLOAD_FOLDER']
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))



@app.route('/', methods=['GET', 'POST'])
def upload_file():

    visitor_ip = request.remote_addr
    unique_visitors.add(visitor_ip)
    visitor_count = len(unique_visitors)
    logging.debug(f'Received request from {visitor_ip} with method {request.method}')


    if request.method == 'POST':

        files = request.files.getlist('file')
        selected_format = request.form['format']
        logging.debug(f'Selected format: {selected_format}')
        logging.debug(f'Files: {", ".join(file.filename for file in files)}')

        if files:
            zip_path = os.path.join(app.config['UPLOAD_FOLDER'], 'converted_images.zip')
            def generate():
                with open(zip_path, 'rb') as f:
                    yield from f
                clear_upload_folder()
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in files:
                    logging.debug(f'Processing file {file.filename} for conversion to {selected_format}')
                    input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    output_path = os.path.splitext(input_path)[0] + '.' + selected_format
                    file.save(input_path)
                    try:
                        convert_image(input_path, output_path, selected_format)
                    except Exception as e:
                        logging.error(f'Error converting image: {e}')
                    try:
                        zipf.write(output_path, os.path.basename(output_path))
                    except Exception as e:
                        logging.error(f'Error writing image to zip: {e}')
                        clear_upload_folder()
                        return render_template('upload.html', error_message='Error writing image to zip')
                    logging.debug(f'Sending ZIP file {zip_path} to client')

            response = Response(generate(), content_type='application/zip')
            response.headers.set('Content-Disposition', 'attachment', filename='converted_images.zip')
            return response

    return render_template('upload.html', visitor_count=visitor_count)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
