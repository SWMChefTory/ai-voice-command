class AudioBuffer:
    def __init__(self):
        self.buffer = bytearray()
    
    def add_audio(self, chunk: bytes):
        self.buffer.extend(chunk)
        
    def pop_audio(self):
        audio_popped = self.buffer;
        self.buffer = bytearray();
        return audio_popped;