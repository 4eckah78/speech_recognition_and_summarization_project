import moviepy.editor as mp
import speech_recognition as sr
import os
from pydub import AudioSegment


def get_text_from_video(path_to_video):
    video = mp.VideoFileClip(path_to_video)

    audio_file = video.audio
    audio_file.write_audiofile("speech.wav")

    r = sr.Recognizer()

    with sr.AudioFile("speech.wav") as source:
        data = r.record(source)
    
    os.remove("speech.wav")

    text = r.recognize_google(data, language="ru-RU")

    return text


def get_text_from_audio(path_to_audio):

    sound = AudioSegment.from_mp3(path_to_audio)
    sound.export("file.wav", format="wav")


    r = sr.Recognizer()

    with sr.AudioFile("file.wav") as source:
        data = r.record(source)

    text = r.recognize_google(data, language="ru-RU")

    os.remove("file.wav")
    return text

if __name__ == "__main__":
    # result = get_text_from_video("russian_video2.mp4")
    result = get_text_from_audio("voice.mp3")
    print(result)