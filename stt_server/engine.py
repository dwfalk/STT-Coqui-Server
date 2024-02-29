import scipy.io.wavfile as wav
from io import BytesIO
from stt import Model

class SpeechToTextEngine:
    def __init__(self, model_path, scorer_path):
        self.model = Model(model_path)
        self.model.enableExternalScorer(scorer_path)

    def run(self, audio):
        audio = BytesIO(audio)
        _, audio = wav.read(audio)
        if len(audio.shape) > 1:
            audio = audio[:, 0]
        result = self.model.stt(audio)
        return result
