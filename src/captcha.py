import speech_recognition as sr
def get_text_from_audio(audio_file):
    r = sr.Recognizer()
    with audio_file as source:
        audio_text = r.record(source)
        text = r.recognize_google(audio_text, language='pt-BR')
    return text
