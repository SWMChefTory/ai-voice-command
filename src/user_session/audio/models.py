class AudioBuffer:
    def __init__(self):
        self.buffer = bytearray()
    
    def add_audio(self, chunk: bytes):
        self.buffer.extend(chunk)
        
    def pop_audio(self):
        audio_popped = self.buffer;
        self.buffer = bytearray();
        return audio_popped;
    
    #샘플 수 반환 (16kHZ, 1 Channel, 16 bits per sample 클로바 STT 스트리밍 참조)
    def get_audio_sample_count(self):
        #2는 16bits per sample 고려
        return len(self.buffer) / 2
    