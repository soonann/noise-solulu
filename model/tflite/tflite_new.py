from flask import Flask, request, jsonify
import numpy as np
import librosa
import tensorflow as tf
import numpy as np

app = Flask(__name__)

# Load the TFLite model
model_path = 'sound_classification.tflite'
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()

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

max_pad_len = 174

def print_probabilities(prediction):
    class_labels = [label_dict[i] for i in range(len(label_dict))]

    for label, prob in zip(class_labels, prediction[0]):
        print(f"{label}:\t{prob:.30f}")


def extract_features(file_name):
    try:
        print("Reading audio file:", file_name)
        audio, sample_rate = librosa.load(file_name, res_type='kaiser_fast')
        print("Audio shape:", audio.shape)
        print("Sample rate:", sample_rate) 
        # Calculate pad length based on max_pad_len or the length of the audio
        pad_len = max_pad_len - audio.shape[0] if audio.shape[0] < max_pad_len else 0
        audio = np.pad(audio, (0, pad_len), mode='constant')[:max_pad_len]
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        pad_width = max_pad_len - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')

        # Compute decibel levels
        rms = librosa.feature.rms(y=audio)[0]
        decibels = abs(np.mean(20 * np.log10(np.abs(rms))))
        #decibels = list(np.abs(decibels))

    except Exception as e:
        print("Error encountered while parsing file: ", file_name)
        print("Error message:", str(e))
        return None, None

    return mfccs, decibels

num_rows = 40
num_columns = 174
num_channels = 1

# Define route for prediction
@app.route('/predict', methods=['POST'])
def predict():
    # Get the audio file from the request
    file = request.files['file']

    # Check if a file was provided
    if file is None or file.filename == '':
        return jsonify({'error': 'No audio file provided.'}), 400

    # Extract features from the audio file
    features, decibels = extract_features(file)

    if features is not None:
        # Reshape the features to match the input shape of the TFLite model
        features = np.expand_dims(features, axis=0)  # Add an extra dimension for the batch size
        features = np.expand_dims(features, axis=3)  # Add an extra dimension for the channels
        features = features.astype(np.float32) 

        # Set the input tensor
        input_index = interpreter.get_input_details()[0]['index']
        interpreter.set_tensor(input_index, features)

        # Run inference
        interpreter.invoke()

        # Get the output tensor
        output_index = interpreter.get_output_details()[0]['index']
        prediction = interpreter.get_tensor(output_index)

        # Get the predicted class label
        predicted_label = int(np.argmax(prediction))
        predicted_class = label_dict.get(predicted_label, 'Unknown')
        
        response_data = {
            'label': predicted_label,
            'class': predicted_class,
            'probabilities': {label: float(prob) for label, prob in zip(label_dict.values(), prediction[0])},
            'decibels': decibels.tolist()
        }

        # Return the predicted class label and class name as a response
        return jsonify(response_data)
    else:
        return jsonify({'error': 'Failed to extract features from audio.'})

if __name__ == '__main__':
    app.run(debug=True)
