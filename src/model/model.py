from kokoro import KPipeline 
import torch

class AudioModel():

    def __init__(self):
        #self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = 'cpu'
        print(f"using device {self.device},use --device flag to override")
        self.pipeline = KPipeline(lang_code='a', device=self.device)
       


    def get_audio_generator(self,full_text):
        """
          use flags to chage voice and and speed
         --voice, --speed
        """
        return self.pipeline(full_text, voice='af_bella', speed=1)
        
