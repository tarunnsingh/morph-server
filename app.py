import os
from flask import Flask, flash, request, redirect, url_for, jsonify, render_template, session, send_file, send_from_directory, safe_join, abort
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from flask_sqlalchemy import SQLAlchemy

from morph import CreateAffineTransform, CreateControlPoints, CreateTriangle, ResizeImage


UPLOAD_FOLDER = './static/uploaded_images'
OUTPUT_FOLDER = './static/output_gif'
MORPH_FRAMES = './static/morph_frames'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
db.init_app(app)


if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
if not os.path.isdir(OUTPUT_FOLDER):
    os.mkdir(OUTPUT_FOLDER)
if not os.path.isdir(MORPH_FRAMES):
    os.mkdir(MORPH_FRAMES)

class IMAGES(db.Model):
    ID = db.Column(db.Integer,primary_key=True)
    NAME1 = db.Column(db.String(300),unique=False)
    NAME2 = db.Column(db.String(300),unique=False)
    IMAGE1 = db.Column(db.BLOB)
    IMAGE2 = db.Column(db.BLOB)
    GIF = db.Column(db.BLOB)


def image_query():
        query = IMAGES.query.order_by(IMAGES.ID.desc()).first()

        image_1 = np.frombuffer(query.IMAGE1, dtype=np.uint8)
        image_2 = np.frombuffer(query.IMAGE2, dtype=np.uint8)

        image_1 = cv2.imdecode(image_1, cv2.IMREAD_COLOR)
        image_2 = cv2.imdecode(image_2, cv2.IMREAD_COLOR)

        return image_1, image_2


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api', methods=['GET'])
def home_page():
    return render_template("index.html")


image_array = []
@app.route('/api/upload', methods=['GET', 'POST'])
def upload_file():
    global image_array
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
            db.create_all()
            image_array.append((filename, file.read()))
            if len(image_array) == 2:
                image_file=IMAGES(
                    NAME1=image_array[0][0],
                    NAME2=image_array[1][0],
                    IMAGE1=image_array[0][1],
                    IMAGE2=image_array[1][1]
                )
                print(image_file)
                db.session.add(image_file)
                db.session.commit()
                image_array = []
                print("File saved to SQLite Server...")
        return jsonify({"Image Uploaded" : filename})




@app.route('/api/morph/<images>', methods=['GET'])
def morph(images):

    image_1, image_2 = image_query()
    resize_images = ResizeImage(image_1, image_2)
    resize_images.resizer()
    image_1, image_2 = image_query()
    image_one = CreateControlPoints(image_1)
    image_two = CreateControlPoints(image_2)
    image_one_control_pts = image_one.create_control_points()
    image_two_control_pts = image_two.create_control_points()
    flash('Control Points Created.', category='info')
    del_tri = CreateTriangle(image_one_control_pts, image_two_control_pts).create_triangles()
    flash('Delaunay Triangles Created.', category='info')
    affine = CreateAffineTransform(del_tri, image_1, image_2, image_one_control_pts, image_two_control_pts)
    affine.perform_affine_transform(40)
    flash('Applied Affine Transform.', category='info')
    try:
        flash('Downloading Now...', category='info')
        print("GIF Created, Initiating Download...")
        return send_from_directory(app.config["OUTPUT_FOLDER"], filename= 'morphed.gif', as_attachment=True)
    except (FileNotFoundError):
        abort(404)



if __name__ == '__main__':
    app.config['SECRET_KEY'] = app.config['SECRET_KEY'] = os.environ.get('SECRET') or 'hyjygjgj'
    app.debug = True
    app.run(threaded = True)
