from uuid import UUID
from src.objectstore.client import ObjectStoreClient
import hashlib
from datetime import datetime
import os

class ObjectStoreService:
    def __init__(self, object_store_client: ObjectStoreClient) -> None:
        self.client = object_store_client
        
    def generate_s3_key(self, session_id: str, filename: str) -> str:
        # 1. 파일명 기반 해시 생성 (SHA256)
        file_hash = hashlib.sha256(filename.encode()).hexdigest()[:16]

        # 2. 현재 날짜시간을 yyyy/mm/dd/HHMMSS 형식으로 생성
        now = datetime.now().strftime("%Y/%m/%d/%H%M%S")

        # 3. 최종 Key 생성
        return f"{session_id}_{file_hash}_{now}"
    
    async def upload_audio(self, session_id :UUID , audio: bytes) -> str:
        file_name = os.getenv("AWS_FILE_NAME")
        if(file_name is None):
            raise Exception("AWS_FILE_NAME is not set")
        self.client.upload_audio(audio, self.generate_s3_key(str(session_id), file_name))
        
        return file_name