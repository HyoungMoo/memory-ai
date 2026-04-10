import speech_recognition as sr


def speech_to_text(language: str = "ko-KR") -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("말씀하세요...")
        audio = recognizer.listen(source, timeout=10)

    return recognizer.recognize_google(audio, language=language)
