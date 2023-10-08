# app.py

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests
import serial

app = Flask(__name__)

load_dotenv()
HOST = "http://ngrok:4040"
PORT=os.getenv('FLASK_PORT')
DEVICE_PATH = os.getenv("DEVICE_PATH")
print(PORT)


def getUrl():
    tunnels = requests.get(os.path.join(HOST, "api/tunnels")).json()['tunnels']
    url = [i for i in tunnels if 'https' in i['public_url']][0]['public_url']
    return url

# @app.after_request
# def apply_caching(response):
    # response.headers["X-Frame-Options"] = "SAMEORIGIN"
    # return response

@app.route('/web')
def index():
    return render_template('index.html')

@app.route('/web/phone')
def phone():
    return render_template('phone.html')

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
        filepath = "audio.webm"
        audio_file.save(filepath)

        return 'Audio received and saved', 200

    return 'Unknown error', 500

@app.route('/webhook',methods = ["POST"])
def getReading():
    # Convert the request data to JSON (assuming it's sent as JSON)
    data = request.json
    print("Received data:", data)

    return jsonify({"message": "Data received successfully!"}),200

@app.route('/web/motor',methods = ["POST"])
def setMotorAngle():
    # Convert the request data to JSON (assuming it's sent as JSON)
    data = request.json
    print("Received data:", data)

    ser = serial.Serial(DEVICE_PATH, 9600)  # open serial port

    # ser.open()
    print(ser.name)         # check which port was really used

    ser.write(b'somestr')     # write a string
    ser.close()             # close port

    return jsonify({"message": "Data received successfully!"}),200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
