import os
from flask import Flask, flash, request, redirect, url_for, jsonify, render_template, session, send_file, send_from_directory, safe_join, abort
from werkzeug.utils import secure_filename
import cv2

from morph import CreateAffineTransform, CreateControlPoints, CreateTriangle, ResizeImage


UPLOAD_FOLDER = './static/uploaded_images'
OUTPUT_FOLDER = './static/output_gif'
MORPH_FRAMES = './static/morph_frames'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
if not os.path.isdir(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)
if not os.path.isdir(MORPH_FRAMES):
    os.mkdir(MORPH_FRAMES)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api', methods=['GET'])
def home_page():
    return render_template("index.html")


@app.route('/api/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print(request.files)
        if ('singleimage' not in request.files):
            print("File not attatched!")
            return jsonify({"File(s) attached": False})
        file = request.files['singleimage']
        if file.filename == '':
            print("File Name is empty.")
            return jsonify({"filename(s)": None})
        if (file and allowed_file(file.filename)):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Files Uploaded', category='info')
            print("File saved to Server...")
            return jsonify({"Image Uploaded" : filename})
            

@app.route('/api/morph/<images>', methods=['GET'])
def morph(images):
    # USE IMAGE HASHED NAMES IN FUTURE
    image_one_path = os.path.join(app.config['UPLOAD_FOLDER'], images.split("|")[0])
    image_two_path = os.path.join(app.config['UPLOAD_FOLDER'], images.split("|")[1])
    resize_images = ResizeImage(image_one_path, image_two_path)
    resize_images.resizer()
    image_one = CreateControlPoints(image_one_path)
    image_two = CreateControlPoints(image_two_path)
    image_one_control_pts = image_one.create_control_points()
    image_two_control_pts = image_two.create_control_points()
    flash('Control Points Created.', category='info')
    del_tri = CreateTriangle(image_one_control_pts, image_two_control_pts).create_triangles()
    flash('Delaunay Triangles Created.', category='info')
    affine = CreateAffineTransform(del_tri, image_one_path, image_two_path, image_one_control_pts, image_two_control_pts)
    affine.perform_affine_transform(40)
    flash('Applied Affine Transform.', category='info')
    try:
        flash('Downloading Now...', category='info')
        print("GIF Created, Initiating Download...")
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename= 'morphed.gif', as_attachment=True)
    except (FileNotFoundError):
        abort(404)



if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.environ.get('SECRET') or 'hyjygjgj'
    app.debug = True
    app.run(host= '0.0.0.0',threaded = True)
