# Base image
FROM python:3.12-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 작업 디렉토리 생성
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && \
    apt-get install -y ffmpeg git libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*

# 종속성 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 코드 복사
COPY . .

# 실행 명령어
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
