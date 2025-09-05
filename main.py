import os
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

def format_image(filename, new_filepath, name, award, date, dims=600):
	im = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	im = ImageOps.exif_transpose(im)
	im = ImageOps.fit(im, (dims, dims))

	canvas = ImageDraw.Draw(im)

	x_padding = 20
	y_buffer = 30
	y_size = 10
	y_offset = 50

    # bottom black 
	canvas.rectangle([(x_padding, dims-(y_buffer+y_size)),
                      (dims-x_padding, dims-y_buffer)], fill='black')
    # top black
	canvas.rectangle([(x_padding, dims-(y_buffer+y_size+y_offset)),
                      (dims-x_padding, dims-(y_buffer+y_offset))], fill='black')

    # middle white
	canvas.rectangle([(x_padding, dims-(y_buffer+y_offset)),
                      (dims-x_padding, dims-(y_buffer+y_size))], fill='white')

    # award text
	canvas.text((x_padding+5, dims-(y_buffer+y_offset-5)), name, font_size=22, fill='black')
	canvas.text((x_padding+200, dims-(y_buffer+y_offset-5)), award, font_size=22, fill='black')
	canvas.text((x_padding+410, dims-(y_buffer+y_offset-5)), date, font_size=22, fill='black')

	im.save(new_filepath)

@app.route('/format/<filename>/<name>/<award>/<date>', methods=['GET', 'POST'])
def download_file(filename, name, award, date):
	old_filename = filename
	filename = name.replace(" ", "-") + "-award-image." + filename.rsplit('.',1)[1];
	filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

	format_image(old_filename, filepath, name, award, date)

	if request.method == 'POST' and 'download' in request.form:
		return send_from_directory(
			os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER']),
			filename,
			as_attachment=True
		)

	return f'''
        <center>
            <h1>Heres your award image</h1>
            <img src="{url_for('static', filename='images/'+filename)}"><br>
            <form method="POST">
                <button type="submit" name="download">Download Award Image</button>
            </form>
        </center>
        '''

"""
POST = format image
GET = display form
"""
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
            return redirect(
				url_for('download_file',
				filename=filename,
				name=request.form['name'],
				award=request.form['award'],
				date=request.form['date'])
			)

    return '''
    <!doctype html>
    <center>
        <title>Award Generator</title>
        <h1>Upload an image</h1>
        <form method=post enctype=multipart/form-data>
            <input type=file name=image><br>
            <input type=text name=name placeholder='name'><br>
            <input type=text name=award placeholder='award'><br>
            <input type=text name=date placeholder='date'><br>
            <input type=submit value=Upload>
        </form>
    </center>
    '''
