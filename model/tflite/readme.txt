To use latest tflite model, `tflite_new.py` which has the updated codes to give a more thorough output.
The output will look like this:
{
    "class": "gun_shot",
    "decibels": 93.50572204589844,
    "label": 6,
    "probabilities": {
        "air_conditioner": 0.0002993291418533772,
        "car_horn": 0.14209860563278198,
        "children_playing": 0.0008355117170140147,
        "dog_bark": 0.03744782507419586,
        "drilling": 0.27139976620674133,
        "engine_idling": 0.006416546180844307,
        "gun_shot": 0.48234423995018005,
        "jackhammer": 0.04258057102560997,
        "siren": 0.016507217660546303,
        "street_music": 7.036227179924026e-05
    }
}

Model Testing score:
Training Accuracy:  0.9352899193763733
Testing Accuracy:  0.8878076672554016
*use the testing accuracy

Concern now:
Librosa may not be good at detecting soft sounds, I have modified the extraction to work reasonably well with the file u provided.

