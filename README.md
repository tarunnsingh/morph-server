<img src="https://cdn.dribbble.com/users/470545/screenshots/2153975/face-morphing.gif" width="300"/>

## Face Morphing (Server Side Script) - See Client Side [Here](https://github.com/tarunnsingh/morph-client).

## Project Demo :nerd_face:

[![IMAGE ALT TEXT HERE](http://img.youtube.com/vi/_ThVHciEj4g/0.jpg)](http://www.youtube.com/watch?v=_ThVHciEj4g)

### What is Morphing? :thinking:

The face morphing algorithm morphs between faces using a common set of feature points, placed by hand on each face. To morph between two faces, you need to warp both faces to a common shape so they can be blended together.

## About this Server. :monocle_face:

This is Flask based API Server, manages the two API Endpoints namely: **POST** `/api/upload` and **GET** `/api/morph/<images>`. The former accepts and a POST request to save an Image to the servers local storage (No Database Connected Yet!). The latter responds to the GET request appended with a unique image name under **<images>**, which basically creates a MORPH of the two images and returns the morphed GIF. On the [client](https://github.com/tarunnsingh/morph-client) repo, ReactJS has been used, however any Frontend framework can be used as per your choice (Angular, Vue etc.).

### Steps for Local Deployment of server: :rocket:

1. Download the 68 facial landmarks predictor by dlib from [here](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2) and extract it to the root directory. It should have the following name : _shape_predictor_68_face_landmarks.dat_.
2. Clone the repo.
3. Open terminal/CMD in repo directory.
4. Create a new virtual environment by `py -m venv env`.
5. Activate the environment by `env\Scripts\activate`.
6. Install the packages by `pip install -r requirements.txt`
7. Start the server by `python app.py`.

### Note: The Server will run on http://localhost:5000, don't forget to add a proxy of this URL in your client side script.

### Contribute

Check and put up Issues and let me know the features which you wish to add before making a PR.

### Leave a :star: if you found this helpful.
