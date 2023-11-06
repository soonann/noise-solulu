# app.py

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
load_dotenv()
EMAIL= os.getenv("EMAIL")
EMAIL_PASSWORD= os.getenv("EMAIL_PASSWORD")
PORT = os.getenv('FLASK_PORT')
DEVICE_PATH = os.getenv("DEVICE_PATH")
SERVO_URL = os.getenv("SERVO_URL")
HOST = "http://ngrok:4040"
print(PORT)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
mail = Mail(app)

app.logger.setLevel(logging.DEBUG)  # Set the log level you want

# Log to a file
handler = logging.FileHandler('flask.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)



def getUrl():
    tunnels = requests.get(os.path.join(HOST, "api/tunnels")).json()['tunnels']
    url = [i for i in tunnels if 'https' in i['public_url']][0]['public_url']
    url = url if "https" in url else url.repalce("http", "https")
    return url


# @app.after_request
# def apply_caching(response):
# response.headers["X-Frame-Options"] = "SAMEORIGIN"
# return response


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error("Unhandled Exception: %s", (e, ))
    return {"error": "Internal Server Error"}, 500


@app.route('/web')
def index():
    return render_template('index.html', ngrok_url=getUrl())


@app.route('/web/phone')
def phone():
    return render_template('phone.html', ngrok_url=getUrl())


@app.route('/web/test')
def test():
    stitch_audio("./audio")


@app.route('/web/audio', methods=['POST'])
def receive_audio():
    # Check if the post request has the file part
    if 'audio' not in request.files:
        return 'No file part', 400

    audio_file = request.files['audio']
    # If the user does not select a file, the browser might
    # submit an empty file without a filename.
    if audio_file.filename == '':
        return 'No selected file', 400

    if audio_file:
        # Save or process the audio file as needed
        # For example, to save the file:
        now = datetime.datetime.now()
        filename = './audio/' + now.strftime('%Y%m%d%H%M%S') + '.webm'
        # filepath = "audio.webm"
        audio_file.save(filename)

        # combined_filename = stitch_audio("./audio")
        app.logger.info(f"audio stored: {filename}")
        # prediction = predict(combined_filename, app.logger)

        # handle servo turning
        # ser = serial.Serial(DEVICE_PATH, 9600)  # open serial port
        # if prediction['label'] == 'neutral':
            # ser.write(f'{1}'.encode())  # turn to 1 degree
        # else:
            # ser.write(f'{80}'.encode())  # turn to 1 degree

        # ser.close()  # close port

        return "Audio file saved", 200

    return "Error you should not be here", 400


@app.route('/web/get/currentaudio', methods=['GET'])
def current_audio():

    try:
        combined_filename = stitch_audio("./audio",app.logger)
    except Exception as e:
        app.logger.info(str(e))
        return jsonify({"decibels":0,"class":"error"}),200
    app.logger.info("Trying to predict audio")
    prediction = predict(combined_filename, app.logger)

    if prediction["decibels"] > 35:
        res = requests.post(url=f"{SERVO_URL}/web/motor",json={"degree":90})
        if res.status_code == 200:
            return jsonify(prediction), 200
        else:
            app.logger.info(res.json)
    return jsonify(prediction), 200


@app.route('/web/grafana', methods=['GET'])
def exporter():
    with open('./mock/mock-0.json', 'r') as json_file:
        data = json.load(json_file)
        # Return the JSON data as a response
        return jsonify([data]), 200

    return jsonify({}), 500

@app.route('/web', methods=['GET'])
def health():
    return jsonify({"health": "ok"}), 200

@app.route('/webhook', methods=["POST"])
def getReading():
    # Convert the request data to JSON (assuming it's sent as JSON)
    data = request.json
    print("Received data:", data)

    return jsonify({"message": "Data received successfully!"}), 200

@app.route('/web/send/petition', methods=["POST"])
def submit_petition():
    
    app.logger.info(request.json)
    # Extract data from form submission
    name = request.json.get('name')
    address = request.json.get('address')
    email = request.json.get('email')
    message = request.json.get('message')
    app.logger.info(os.getenv("EMAIL"))
    # Create the message
    # Send the message
    try:
        msg = Message("We Received Your Petition",
                    sender=EMAIL,
                    recipients=[email])
        msg.body = f"Hello {name},\n\nWe have received your petition. Here are the details we got:\nName: {name}\nAddress: {address}\nMessage: {message}\n\nThank you!"
        msg.html = f"<p>Hello <strong>{name}</strong>,</p><p>We have received your petition. Here are the details we got:</p><ul><li>Name: {name}</li><li>Address: {address}</li><li>Message: {message}</li></ul><p>Thank you!</p>"

    
        mail.send(msg)
        return jsonify(success=True, message="Email sent successfully.")
    except Exception as e:
        app.logger.info(e)
        return jsonify(success=False, message=str(e)), 500


@app.route('/web/motor', methods=["POST"])
def setMotorAngle():
    data = request.json
    if data["degree"] is None:
        return jsonify({"message": "Invalid input"}, 400)

    ser = serial.Serial(DEVICE_PATH, 9600)  # open serial port
    ser.write(f'{data["degree"]}'.encode())  # write a string
    ser.close()  # close port

    return jsonify({"message": "Data received successfully!"}), 200

@app.route('/web/reset', methods=["GET"])
def datareset():
    with TinyDB('db.json') as db:
        db.truncate()
        mock_data = generate_mock_data(users=10)
        for data in mock_data:
            db.insert(data)
    return "Db reset", 200
    
@app.route('/web/get', methods=["GET"])
def data_get_all():

    with TinyDB('db.json') as db:
        data = db.all()
    return jsonify(data), 200

@app.route('/web/recommendation/get', methods=["GET"])
def data_recommendation_get():
    with TinyDB('db.json') as db:
        chosen_data = db.all()[0]
    flat_data = [entry for entry in chosen_data['data']]
    quiet_periods, active_periods = analyze_noise_data(flat_data)
    
    nap_recommendations = get_clustered_recommendations(quiet_periods, eps_duration=60, min_duration=30)
    going_out_recommendations = get_clustered_recommendations(active_periods, eps_duration=120, min_duration=30)

    return jsonify({
        "nap":nap_recommendations,
        "go_out":going_out_recommendations
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
