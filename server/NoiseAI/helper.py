import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import librosa
from flask import Flask, request, jsonify

import csv
import scipy
from IPython.display import Audio
from scipy.io import wavfile

model = hub.load("https://tfhub.dev/google/yamnet/1")


# Find the name of the class with the top score when mean-aggregated across frames.
def class_names_from_csv(class_map_csv_text):
  """Returns list of class names corresponding to score vector."""
  class_names = []
  with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
      class_names.append(row['display_name'])

  return class_names

def ensure_sample_rate(original_sample_rate, waveform,
                       desired_sample_rate=16000):
  """Resample waveform if required."""
  if original_sample_rate != desired_sample_rate:
    desired_length = int(round(float(len(waveform)) /
                               original_sample_rate * desired_sample_rate))
    waveform = scipy.signal.resample(waveform, desired_length)
  return desired_sample_rate, waveform


class_map_path = model.class_map_path().numpy()
class_names = class_names_from_csv(class_map_path)


def predict(file,logger):
    audio, sample_rate = librosa.load(file, sr=16000, mono=True)
    
    # Get the amplitude of the audio
    S = np.abs(librosa.stft(audio))

    # Convert the amplitude to decibels using the smallest possible non-zero value encoded by the bit depth as the reference
    # For 16-bit audio, this would be 1/32768
    ref_value = 1/32768

    # Convert to decibels
    db = librosa.amplitude_to_db(S, ref=ref_value)
    # Calculate the mean decibel level across the entire audio clip relative to absolute silence
    decibels = int(np.mean(db))
    logger.info(decibels)
    if decibels > 45:
        try:
            scores, embeddings, spectrogram = model(audio)
            scores_np = scores.numpy()
            spectrogram_np = spectrogram.numpy()
            infered_class = class_names[scores_np.mean(axis=0).argmax()]

        except Exception as e:
           logger.info(str(e))
        response_data = {
            'class': infered_class,
            'decibels': decibels
        }
    else:
        response_data = {
            'class': "Silence",
            'decibels': decibels
        }

    logger.info(response_data)

        # Return the predicted class label and class name as a response
    return response_data
    
