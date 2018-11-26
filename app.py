import json
import os

from flask import (Flask, Response, jsonify, request, send_from_directory,
                   url_for)

from utils import random_name, plot_that, async_plot

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uplodas'
app.config['DEBUG'] = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    """List of routes for this API."""
    output = {
            'Post dip and strike': 'POST /plot',
            'Download specific filename': 'GET /download/{filename}',
            }
    
    response = jsonify(output)
    return response

@app.route('/plot/', methods=['POST'])
@app.route('/plot', methods=['POST'])
def plot():
    """GET dip and strike from the user and save the output"""

    needed = ['dip', 'strike']

    if request.content_type == 'application/json':
        data = request.get_json(force=True)
    else:
        data = request.form

    if all([key in data for key in needed]):
        try:
            dip = int(data.get('dip'))
            strike = int(data.get('strike'))
        except:
            return jsonify({'message':'dip and strike should be integer.'}), 400
        filename = async_plot(dip, strike)
        #filename = plot_that(dip, strike)
        #filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
        response = Response(
                response=json.dumps({'filename': filename}),
                mimetype="application/json",
                status=201
                )
    else:
        response = Response(
            mimetype="application/json",
            response=json.dumps({'message': 'dip and strike cannot left be blank!'}),
            status=400
            )
    return response

@app.route('/download/', methods=['GET'])
@app.route('/download/<path:filename>', methods=['GET'])
def download(filename=None):
    if filename:
        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
        else:
            return jsonify({'message':"File '{}' does not exist.".format(filename)}), 404
    return jsonify({'message':'filename cannot left be blank!'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
