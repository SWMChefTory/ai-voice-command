from mypy_boto3_s3.client import S3Client
import boto3, os
import wave
import io
from uvicorn.main import logger

class ObjectStoreClient:
    def __init__(self) -> None:
        self.s3: S3Client = boto3.client( # pyright: ignore
                "s3",
                region_name=os.getenv("AWS_REGION"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
            )
        
    def pcm_to_wav(self, pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1, sample_width: int = 2) -> bytes:
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(sample_width)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(pcm_bytes)
        return wav_buffer.getvalue()
    
    def upload_audio(self, audio: bytes, key: str) -> None:
        bucket_name = os.getenv("AWS_BUCKET_NAME")
        logger.info(f"Uploading audio to {bucket_name}")
        if(bucket_name is None):
            raise Exception("AWS_BUCKET_NAME is not set")
        
        self.s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=audio
        )
    
    