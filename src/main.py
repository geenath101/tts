from model.model import AudioModel
from model.file_reader import FileReader
import application
import sys
import logging

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("fitz").setLevel(logging.WARNING)

    logging.getLogger(__name__).info("application started")
    model = AudioModel()
    file =  FileReader("./resources/Geenath_cover_letter.pdf")
    file_content = file.get_content_as_string()
    print(f"file content size {sys.getsizeof(file_content)}")
    audio_generator = model.get_audio_generator(file_content)
    application.start_listening_cool(audio_generator)
    
