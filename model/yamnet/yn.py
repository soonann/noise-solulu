import tensorflow_hub as hub
import tensorflow as tf
import numpy as np
import librosa
from flask import Flask, request, jsonify

import csv
import scipy
from IPython.display import Audio
from scipy.io import wavfile

app = Flask(__name__)

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

@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']
    audio, sample_rate = librosa.load(file, sr=16000, mono=True)
    scores, embeddings, spectrogram = model(audio)

    scores_np = scores.numpy()
    spectrogram_np = spectrogram.numpy()
    infered_class = class_names[scores_np.mean(axis=0).argmax()]
    return jsonify({"class": infered_class})
    #print(f'The main sound is: {infered_class}')

if __name__ == '__main__':
  app.run(debug=True)