from model.model import AudioModel
from model.file_reader import FileReader
import application
import sys

if __name__ == "__main__":
    print(f"application started")
    model = AudioModel()
    file =  FileReader("./resources/Geenath_cover_letter.pdf")
    file_content = file.get_content_as_string()
    print(f"file content size {sys.getsizeof(file_content)}")
    audio_generator = model.get_audio_generator(file_content)
    application.start_listening_cool(audio_generator)
    
