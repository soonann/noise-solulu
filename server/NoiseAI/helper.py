import numpy as np
import librosa
import tensorflow as tf
import os
from tensorflow import keras

max_pad_len = 174
num_rows = 40
num_columns = 174
num_channels = 1

# Define the label dictionary for mapping label indices to class names
label_dict = {
    0: 'air_conditioner',
    1: 'car_horn',
    2: 'children_playing',
    3: 'dog_bark',
    4: 'drilling',
    5: 'engine_idling',
    6: 'neutral',
    7: 'jackhammer',
    8: 'siren',
    9: 'street_music'
}

model_path = os.path.join(os.path.dirname(__file__), 'models/sound_classification.tflite')
interpreter = tf.lite.Interpreter(model_path=model_path)
interpreter.allocate_tensors()



# def extract_features(filename,logger):
#     try:
#         logger.info("Reading audio data...")
#         audio, sample_rate = librosa.load(filename)
        
#         mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
#         pad_width = max_pad_len - mfccs.shape[1]
#         mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')

#         return mfccs
#     except Exception as e:
#         logger.info("Error encountered while parsing the audio data.")
#         assert e
    


# def predict(filename,logger):

    
#     # Extract features from the stitched audio data
#     features = extract_features(filename,logger)
#     logger.info(features.shape)

#     if features is not None:
#         # Reshape the features to match the input shape of the model
#         features = features.reshape(1, num_rows, num_columns, num_channels)

#         # Predict the class of the audio file
#         prediction = model.predict(features)
#         logger.info(prediction)
#         # Get the predicted class label
#         predicted_label = int(np.argmax(prediction))
#         predicted_class = label_dict.get(predicted_label, 'Unknown')

#         # Return the predicted class label and class name as a response
#         return {'label': predicted_label, 'class': predicted_class}
#     else:
#         return {'error': 'Failed to extract features from audio.'}
    


def extract_features(file_name,logger):
    try:
        print("Reading audio file:", file_name)
        logger.info(("Reading audio file:", file_name))
        audio, sample_rate = librosa.load(file_name)

        # Calculate pad length based on max_pad_len or the length of the audio
        pad_len = max_pad_len - audio.shape[0] if audio.shape[0] < max_pad_len else 0
        audio = np.pad(audio, (0, pad_len), mode='constant')[:max_pad_len]
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        pad_width = max_pad_len - mfccs.shape[1]
        mfccs = np.pad(mfccs, pad_width=((0, 0), (0, pad_width)), mode='constant')

        # Compute decibel levels
        rms = librosa.feature.rms(y=audio)[0]
        pressure = np.sqrt(np.mean(np.square(audio)))
        reference_pressure = 20e-6
        decibels = 20 * np.log10(pressure / reference_pressure)
        #decibels = list(np.abs(decibels))

    except Exception as e:
        print("Error encountered while parsing file: ", file_name)
        print("Error message:", str(e))
        return None, None

    return mfccs, decibels


def predict(file,logger):
    features, decibels = extract_features(file,logger)

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
        predicted_label = np.argmax(prediction)
        predicted_class = label_dict.get(predicted_label, 'Unknown')
        
        response_data = {
            'label': predicted_label,
            'class': predicted_class,
            'probabilities': {label: float(prob) for label, prob in zip(label_dict.values(), prediction[0])},
            'decibels': decibels.tolist()
        }

        logger.info(response_data)

        # Return the predicted class label and class name as a response
        return response_data
    else:
        return {'error': 'Failed to extract features from audio.'}
