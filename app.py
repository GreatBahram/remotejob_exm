import json
import os

from matplotlib import pyplot as plt
from flask import (Flask, Response, jsonify, request, send_from_directory,
                   url_for)
import mplstereonet

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uplodas'
app.config['DEBUG'] = False

image_format = 'png'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def random_name():
    """Return picture absolute path and also filename"""
    filename = os.urandom(15).hex()
    filename = filename + '.' + image_format
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    return picture_path, filename

def plot_that(dip, strike):
    """ Plot the figure and save into app.config['UPLOAD_FOLDER'] directory """
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='stereonet')
    strike, dip = strike, dip
    ax.plane(strike, dip, 'g-', linewidth=2)
    ax.pole(strike, dip, 'g^', markersize=18)
    ax.rake(strike, dip, -25)
    ax.grid()
    picture_path, filename = random_name()
    plt.close('all')
    fig.savefig(picture_path, dpi=200, format=image_format)

    return filename

@app.route('/')
def index():
    """List of routes for this API."""
    output = {
        'Post dip and strike': 'POST /plot',
        'Download an image': 'GET /download/<filename>',
    }
    response = jsonify(output)
    return response

@app.route('/plot', methods=['POST'])
def plot():
    """GET dip and strike from the user and save the output"""
    needed = ['dip', 'strike']
    if all([key in request.form for key in needed]):
        try:
            dip = int(request.form['dip'])
            strike = int(request.form['strike'])
        except:
            print('something bad happend')
        filename = plot_that(dip, strike)
        response = Response(
                response=json.dumps({'message': 'Plot has been created', 'filename': filename}),
                mimetype="application/json",
                status=201
                )
    else:
        response = Response(
            mimetype="application/json",
            response=json.dumps({'message': 'dip and strike cannot left be blank!'}),
            status=404
            )
    return response

@app.route('/download/<filename>')
def downloed_file(filename):
    """Download a file."""
    uploads = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    if os.path.exists(os.path.join(uploads, filename)):
        return send_from_directory(directory=uploads, filename=filename)
    else:
        return jsonify({'message': "File does not found"}), 404

if __name__ == '__main__':
    app.run()
