from pydub import AudioSegment
import os
import datetime
import io

def stitch_audio(directory,seconds=3):

    # Get all filenames in the directory
    all_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Sort filenames
    all_files.sort(key=lambda x:int(x.split(".")[0]))

    # Ensure we have at least 3 files
    if len(all_files) < seconds:
        return "Not enough audio files to combine."

    # Load the last 3 audio files
    filepaths = [os.path.join(directory, all_files[i]) for i in range(-seconds,0,1)]
    audios = list(map(lambda x:AudioSegment.from_file(x,format="webm"),filepaths))
    def stitch(audio_list):
        if len(audio_list)>0:
            temp = audio_list[0]
            for audio in audio_list[1:]:
                temp += audio
        return temp

    # audio1 = AudioSegment.from_file(os.path.join(directory, all_files[-3]),format="webm")
    # audio2 = AudioSegment.from_file(os.path.join(directory, all_files[-2]),format="webm")
    # audio3 = AudioSegment.from_file(os.path.join(directory, all_files[-1]),format="webm")

    # Combine the audio files
    combined = stitch(audios)

    # Output the combined audio
    now = datetime.datetime.now()
    filename = './audio/combined/'+now.strftime('%Y%m%d%H%M%S')+'_combine.webm'
    combined.export(filename, format="webm")

    return filename

    


# Example usage
# stitch_last_three_audio("/path/to/directory/with/audio/files")
