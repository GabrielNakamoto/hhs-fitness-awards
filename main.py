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

def format_image(filename, new_filepath, name, award, date):
	width, height = (600, 500)

	im = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], filename))
	im = ImageOps.exif_transpose(im)
	im = ImageOps.fit(im, (width, height))

	draw = ImageDraw.Draw(im)

	x_pad, y_pad = (20, 30)
	r_thickness = 10
	r_offset = 50
	t_pad = (r_offset / 2) + 11

	name_delta = 10
	award_delta = int(width * 0.33) + name_delta
	date_delta = int(width * 0.66) + name_delta

	draw.rectangle([
		x_pad,
		height - y_pad - r_thickness,
		width - x_pad,
		height - y_pad
	], fill='black')

	draw.rectangle([
		x_pad,
		height - y_pad - r_offset - r_thickness,
		width - x_pad,
		height - y_pad - r_offset
	], fill='black')

	draw.rectangle([
		x_pad,
		height - y_pad - r_offset,
		width - x_pad,
		height - y_pad - r_thickness
	], fill='white')

	draw.text((x_pad + name_delta, height - y_pad - r_thickness - t_pad),
		name,
		font_size=22,
		fill='black'
	)
	draw.text((x_pad + award_delta, height - y_pad - r_thickness - t_pad),
		award,
		font_size=22,
		fill='black'
	)
	draw.text((x_pad + date_delta, height - y_pad - r_thickness - t_pad),
		date,
		font_size=22,
		fill='black'
	)

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
		<h3>Let me know if you encounter any issues, at <a href="mailto:gabriel@nakamoto.ca">gabriel@nakamoto.ca</a></h3>
        <form method=post enctype=multipart/form-data>
            <input type=file name=image><br>
            <input type=text name=name placeholder='name'><br>
            <input type=text name=award placeholder='award'><br>
            <input type=text name=date placeholder='date'><br>
            <input type=submit value=Upload>
        </form>
    </center>
    '''
