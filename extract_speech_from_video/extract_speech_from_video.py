import moviepy.editor as mp
import speech_recognition as sr
import os


def get_text_from_video(path_to_video):
    video = mp.VideoFileClip(path_to_video)

    audio_file = video.audio
    audio_file.write_audiofile("speech.wav")

    r = sr.Recognizer()

    with sr.AudioFile("speech.wav") as source:
        data = r.record(source)
    
    os.remove("speech.wav")

    text = r.recognize_google(data, language="ru-RU")

    print(text)
    return text

if __name__ == "__main__":
    result = get_text_from_video("russian_video2.mp4")