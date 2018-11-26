import contextlib
import os
from hashlib import md5
from threading import Thread

import mplstereonet
from flask import current_app
from matplotlib import pyplot as plt
from openpyxl import Workbook

IMAGE_FMT = 'png'


def random_name(dip, strike):
    """Return picture absolute path and also filename"""
    filename = md5('{}{}'.format(dip, strike).encode('utf-8')).hexdigest()
    filename = filename + '.' + IMAGE_FMT
    picture_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    return picture_path, filename


def plot_that(dip, strike, picture_path):
    """ Plot the figure and save into app.config['UPLOAD_FOLDER'] directory """
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='stereonet')
    ax.plane(strike, dip, 'g-', linewidth=2)
    ax.pole(strike, dip, 'g^', markersize=18)
    ax.rake(strike, dip, -25)
    ax.grid()
    #picture_path, filename = random_name()
    plt.close('all')
    fig.savefig(picture_path, dpi=200, format=IMAGE_FMT)
    #return filename

def custom_plot(dip, strike):
    """ Plot the figure and save into app.config['UPLOAD_FOLDER'] directory """
    plunge, bearing = dip, strike
    fig = plt.figure()
    ax = fig.add_subplot(121, projection='stereonet')
    line = ax.plane(strike, dip, 'g-', linewidth=2)
    triangle = ax.pole(strike, dip, 'g^', markersize=18)
    blue_point = ax.rake(strike, dip, -25)
    orange_point = ax.line(plunge, bearing)
    return (line , triangle, blue_point, orange_point)
    


def async_plot(dip, strike):
    """ Run plot_that function with another thread in order to make the program faster"""
    picture_path, filename = random_name(dip, strike)
    Thread(target=plot_that, args=(dip, strike, picture_path,)).start()
    return filename

@contextlib.contextmanager
def excel_handler(filename):
    wb = Workbook()
    yield wb 
    wb.save(filename)
    wb.close()
