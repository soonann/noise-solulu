# app.py

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)

load_dotenv()
HOST = "http://ngrok:4040"
HOST2 =  "http://ngrok2:4040"
PORT=os.getenv('FLASK_PORT')
print(PORT)


def getUrl():
    tunnels = requests.get(os.path.join(HOST, "api/tunnels")).json()['tunnels']
    url = [i for i in tunnels if 'https' in i['public_url']][0]['public_url']
    return url

def getUrl2():
    tunnels = requests.get(os.path.join(HOST2, "api/tunnels")).json()['tunnels']
    url = [i for i in tunnels if 'https' in i['public_url']][0]['public_url']
    return url


@app.route('/')
def index():
    url1 = getUrl()
    url2 = getUrl2()
    print(url1,url2)
    return render_template('index.html',ngrok_url = url1, ngrok2_url = url2)

@app.route('/phone')
def phone():
    return render_template('phone.html',ngrok_url = getUrl())

@app.route('/audio', methods=['POST'])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)
