import json
import os
from hashlib import md5

import requests
from flask import (Flask, Response, jsonify, request, send_from_directory,
                   url_for)
from utils import (async_plot, custom_plot, excel_handler, plot_that,
                   random_name)

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uplodas'
app.config['DEBUG'] = False

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET'])
def index():
    """List of routes for this API."""
    output = {
            'Post dip and strike': 'POST /plot',
#            'Download specific filename': 'GET /download/{filename}',
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
        filename = md5('{}{}'.format(dip, strike).encode('utf-8')).hexdigest() + '.xlsx'
        print(filename)
        line , triangle, blue_point, orange_point = custom_plot(dip, strike)
        with excel_handler(filename) as wb:
            # write basic information
            work_sheet = wb.active
            work_sheet['A1'] =  'Dip'
            work_sheet['B1'] =  'Strike'
            work_sheet['A2'] =  dip
            work_sheet['B2'] =  strike
            work_sheet.title = 'Data'

            # write output of the program
            work_sheet = wb.create_sheet('Plane points')
            a, b = line[0].get_data()
            work_sheet['A1'] = 'A'
            work_sheet['B1'] = 'B'
            for index, (a_data, b_data) in enumerate(zip(a, b)):
                work_sheet.cell(row=index+2, column=1).value = a_data
                work_sheet.cell(row=index+2, column=2).value = a_data

            work_sheet = wb.create_sheet('Pole points')
            x, y = triangle[0].get_data()
            work_sheet['A1'] = 'x'
            work_sheet['B1'] = 'y'
            work_sheet['A2'] = x[0]
            work_sheet['B2'] = y[0]

            work_sheet = wb.create_sheet('Rake points')
            x, y = blue_point[0].get_data()
            work_sheet['A1'] = 'x'
            work_sheet['B1'] = 'y'
            work_sheet['A2'] = x[0]
            work_sheet['B2'] = y[0]

            work_sheet = wb.create_sheet('Line points')
            x, y = orange_point[0].get_data()
            work_sheet['A1'] = 'x'
            work_sheet['B1'] = 'y'
            work_sheet['A2'] = x[0]
            work_sheet['B2'] = y[0]

        # post data into Kashef.io
        output = requests.post("http://kcs.kashef.io/upload/", files={"file":open(filename,'rb')})
        if 'url' in output.json():
            message = 'Data has been saved.'
            response = Response(
                    response=json.dumps({'message': message}),
                    mimetype="application/json",
                    status=201)
        else:
            message = 'Something bad happended during upload file into kashef'
            response = Response(
                    response=json.dumps({'message': message}),
                    mimetype="application/json",
                    status=400)
        # save the pircture and return filename
        #filename = async_plot(dip, strike)
        #filename = plot_that(dip, strike)
        #filepath = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename)
    else:
        response = Response(
            mimetype="application/json",
            response=json.dumps({'message': 'dip and strike cannot left be blank!'}),
            status=400
            )
    return response

#@app.route('/download/', methods=['GET'])
#@app.route('/download/<path:filename>', methods=['GET'])
#def download(filename=None):
#    if filename:
#        if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
#            return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
#        else:
#            return jsonify({'message':"File '{}' does not exist.".format(filename)}), 404
#    return jsonify({'message':'filename cannot left be blank!'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
