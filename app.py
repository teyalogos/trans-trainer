import os
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_socketio import SocketIO, send, emit
from werkzeug.utils import secure_filename
from rpy2.robjects.packages import STAP
from keras.models import load_model
import tensorflow as tf
from sklearn.preprocessing import normalize
import numpy as np

# load R functions
with open('preprocess.r', 'r') as f:
    string = f.read()
preprocess = STAP(string, "preprocess")

# load Keras model 1 and setup tensorflow
graph = tf.get_default_graph()
model_main = load_model("models/final.hdf5")

# flask setup
UPLOAD_FOLDER = 'audio'
ALLOWED_EXTENSIONS = set(['wav'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="threading")


def predict(filename):
    """Runs filename (a WAV file) through our neural network for classification"""

    # preprocess data
    data = preprocess.processAudio(filename)
    unprocessed_data = list(data)
    data = list(data)
    data = np.array([data])
    data = normalize(data)

    # predict
    with graph.as_default():
        prediction = model_main.predict_proba(data)

    return {'prediction': prediction.tolist(), 'data': unprocessed_data}


def allowed_file(filename):
    """Checks if filename is an allowed filetype"""

    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def homepage():

    # uploads fies when POST message is received
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            # if the user has not sleected a file
            flash('No selected file')
            return redirect(request.url)

        if file and not allowed_file(file.filename):
            # sends message to client that the file submitted is invalid
            socketio.emit(
                'filestatus', {'data': 'is-invalid'}, namespace='/voice')

        if file and allowed_file(file.filename):
            # if the user has selected a valid file, upload file
            socketio.emit(
                'filestatus', {'data': 'is-valid'}, namespace='/voice')
            socketio.emit(
                'progress', {'width': 33, 'text': 'Uploading File'}, namespace='/voice')

            filename = secure_filename(file.filename)
            filename_path = os.path.join(
                app.config['UPLOAD_FOLDER'], filename).replace("\\", "/")
            file.save('static/' + filename_path)

            # run specified file through neural network
            socketio.emit(
                'progress', {'width': 66, 'text': 'Running Tests'}, namespace='/voice')
            stats = predict('static/' + filename_path)
            # send a message back to the client containing the results
            socketio.emit('prediction', stats, namespace='/voice')
            socketio.emit(
                'progress', {'width': 100, 'text': 'Displaying Results'}, namespace='/voice')

    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app)
