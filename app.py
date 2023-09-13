# app.py

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook',methods = ["POST"])
def getReading():
    # Convert the request data to JSON (assuming it's sent as JSON)
    data = request.json
    print("Received data:", data)

    return jsonify({"message": "Data received successfully!"}),200

if __name__ == '__main__':
    app.run(port=6969, debug=True)
