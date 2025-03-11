from SpeechRecognition import audio, recognition
from TextToSpeech import Humanized
from TextToSpeech import lite

if __name__ == "__main__":
    while True:
        print("🎙️ Habla ahora...")
        text = recognition.trascribe_from_file(audio.file_voice())
        #Humanized.humanizedText(text,"es")
        lite.text_to_speech(text)

      