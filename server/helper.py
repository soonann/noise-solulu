from pydub import AudioSegment
import os

def stitch_last_three_audio(directory):
    # Get all filenames in the directory
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Sort filenames
    all_files.sort()

    # Ensure we have at least 3 files
    if len(all_files) < 3:
        return "Not enough audio files to combine."

    # Load the last 3 audio files
    audio1 = AudioSegment.from_file(os.path.join(directory, all_files[-3]),format="webm")
    audio2 = AudioSegment.from_file(os.path.join(directory, all_files[-2]),format="webm")
    audio3 = AudioSegment.from_file(os.path.join(directory, all_files[-1]),format="webm")

    # Combine the audio files
    combined = audio1 + audio2 + audio3

    # Output the combined audio
    combined.export("combined_output.webm", format="webm")


# Example usage
# stitch_last_three_audio("/path/to/directory/with/audio/files")
