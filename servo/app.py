from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv
from helper import stitch_audio
from NoiseAI import *
from tinydb import TinyDB, Query
from mock import *
from actionable import *

import json
import logging
import os
import requests
import serial
import datetime

app = Flask(__name__)


app.logger.setLevel(logging.DEBUG)  # Set the log level you want


load_dotenv()
HOST = "http://ngrok:4040"
PORT = os.getenv('FLASK_PORT')
DEVICE_PATH = os.getenv('DEVICE_PATH')


@app.route('/web/motor', methods=["POST"])
def setMotorAngle():
    data = request.json
    if data["degree"] is None:
        return jsonify({"message": "Invalid input"}, 400)

    ser = serial.Serial(DEVICE_PATH, 9600)  # open serial port
    ser.write(f'{data["degree"]}'.encode())  # write a string
    ser.close()  # close port

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)