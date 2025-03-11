from SpeechRecognition import audio, recognition

if __name__ == "__main__":
    print(recognition.trascribe_from_file(audio.file_voice()))
