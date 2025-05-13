# Base image
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR .

# 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY app/ .

# gdown 먼저 설치
RUN pip install --no-cache-dir gdown

# 필수 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y ffmpeg git libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# 모델 파일 다운로드
RUN mkdir -p Wav2Lip/checkpoints && \
    gdown https://drive.google.com/uc?export=download&id=1ZQwe70j4l6qZ4ea4ERFFLxTZoyK-21hb -O Wav2Lip/checkpoints/wav2lip_gan.pth && \
    mkdir -p Wav2Lip/face_detection/detection/sfd && \
    gdown https://drive.google.com/uc?export=download&id=1bTfcdIBbQT1ipbbZ-mzarP_Mq0MSuOP5 -O Wav2Lip/face_detection/detection/sfd/s3fd.pth

# 포트 및 실행
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
