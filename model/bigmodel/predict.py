from flask import Flask, request, jsonify
import numpy as np
import librosa
import tensorflow as tf
from tensorflow import keras

app = Flask(__name__)

# Load the saved model
model = tf.keras.models.load_model('sound_classification.hdf5')

# Define the label dictionary for mapping label indices to class names
label_dict = {
    0: 'air_conditioner',
    1: 'car_horn',
    2: 'children_playing',
    3: 'dog_bark',
    4: 'drilling',
    5: 'engine_idling',
    6: 'gun_shot',
    7: 'jackhammer',
    8: 'siren',
    9: 'street_music'
}

import numpy as np
max_pad_len = 174

def extract_features(file_name):
    try:
        print("Reading audio file:", file_name)
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
        print("Audio shape:", audio.shape)
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        pad_width = max_pad_len - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')
    except Exception as e:
        print("Error encountered while parsing file: ", file_name)
        return None
    return mfccs

num_rows = 40
num_columns = 174
num_channels = 1

# Define the route for predicting audio
@app.route('/predict', methods=['POST'])
def predict():
    # Get the audio file from the request
    file = request.files['file']

    # Extract features from the audio file
    features = extract_features(file)
    print("Features shape:", features.shape)

    if features is not None:
        # Reshape the features to match the input shape of the model
        features = features.reshape(1, num_rows, num_columns, num_channels)

        # Predict the class of the audio file
        prediction = model.predict(features)

        # Get the predicted class label
        predicted_label = int(np.argmax(prediction))
        predicted_class = label_dict.get(predicted_label, 'Unknown')

        # Return the predicted class label and class name as a response
        return jsonify({'label': predicted_label, 'class': predicted_class})
    else:
        return jsonify({'error': 'Failed to extract features from audio.'})

if __name__ == '__main__':
    app.run(debug=True)
