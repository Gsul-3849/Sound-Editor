import pydub
from pydub import AudioSegment

class AudioUtils:
    def __init__(self):
        pass

    #Split Song
    def interval(self, audio_segment, start_time=0, end_time=None):
        start_ms = int(start_time * 1000)

        if end_time is None:
            return audio_segment[start_ms:]

        end_ms = int(end_time * 1000)
        return audio_segment[start_ms:end_ms]

    

    #Adjust Volume
    def increase_volume(self, audio_segment, db):
        return audio_segment + db
    def decrease_volume(self, audio_segment, db):
        return audio_segment - db

    #Join Songs
    def join_songs(self, audio1, audio2):
        return audio1 + audio2