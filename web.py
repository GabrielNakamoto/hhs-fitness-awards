import os
from datetime import date
from PIL import Image, ImageOps, ImageDraw
from flask import Flask, request, redirect, flash, url_for, send_from_directory
from werkzeug.utils import secure_filename
    
app = Flask(__name__)

UPLOAD_FOLDER = 'static/images/'
FILETYPES = ['png', 'jpeg', 'jpg']

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in FILETYPES

@app.route('/uploads/<filename>/<name>/<award>', methods=['GET', 'POST'])
def download_file(filename, name, award):
    # process image
    im = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    im = ImageOps.fit(im, (600, 600))

    canvas = ImageDraw.Draw(im)

    x_padding = 20
    y_buffer = 30
    y_size = 10
    y_offset = 50

    # bottom black 
    canvas.rectangle([(x_padding, 600-(y_buffer+y_size)),
                      (600-x_padding, 600-y_buffer)], fill='black')
    # top black
    canvas.rectangle([(x_padding, 600-(y_buffer+y_size+y_offset)),
                      (600-x_padding, 600-(y_buffer+y_offset))], fill='black')

    # middle white
    canvas.rectangle([(x_padding, 600-(y_buffer+y_offset)),
                      (600-x_padding, 600-(y_buffer+y_size))], fill='white')

    # award text
    canvas.text((x_padding+20, 600-(y_buffer+y_offset-5)), name, font_size=25, fill='black')
    canvas.text((x_padding+200, 600-(y_buffer+y_offset-5)), award, font_size=25, fill='black')
    canvas.text((x_padding+400, 600-(y_buffer+y_offset-5)), str(date.today()), font_size=25, fill='black')

    filename = filename.rsplit('.',1)[0] + '-processed.' + filename.rsplit('.',1)[1]
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if request.method == 'POST':
        if 'download' in request.form:
            return send_from_directory(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']), filename)

    im.save(filepath)
    return f'''
        <center>
            <h1>Heres your award image</h1>
            <img src="{url_for('static', filename='images/'+filename)}"><br>
            <form method="POST">
                <button type="submit" name="download">Download Award Image</button>
            </form>
        </center>
        '''

@app.route("/", methods=['GET', 'POST'])
def run():
    if request.method == 'POST':
        # check if request has file
        if 'image' not in request.files:
            print("Image not provided in POST request")
            return redirect(request.url)
            
        image = request.files['image']
        if image.filename == '':
            print("Empty file")
            return redirect(request.url)

        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', filename=filename, name=request.form['name'], award=request.form['award']))

    return '''
    <!doctype html>
    <center>
        <title>Award Generator</title>
        <h1>Upload an image</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=image><br>
            <input type=text name=name placeholder='name'><br>
            <input type=text name=award placeholder='award'><br>
            <input type=submit value=Upload>
        </form>
    </center>
    '''
