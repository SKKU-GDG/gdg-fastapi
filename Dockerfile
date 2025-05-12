# Base image
FROM python:3.12-slim

# 필수 패키지 설치 (gdown 포함)
RUN apt-get update && \
    apt-get install -y ffmpeg git libgl1-mesa-glx && \
    pip install --no-cache-dir gdown && \
    rm -rf /var/lib/apt/lists/*
    
# 작업 디렉토리 생성
WORKDIR /app

# 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 모델 파일 다운로드
RUN mkdir -p app/Wav2Lip/checkpoints && \
    gdown https://drive.google.com/file/d/1ZQwe70j4l6qZ4ea4ERFFLxTZoyK-21hb -O app/Wav2Lip/checkpoints/wav2lip_gan.pth && \
    mkdir -p app/Wav2Lip/face_detection/detection/sfd && \
    gdown https://drive.google.com/file/d/1bTfcdIBbQT1ipbbZ-mzarP_Mq0MSuOP5 -O app/Wav2Lip/face_detection/detection/sfd/s3fd.pth

# 실행 명령어
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
