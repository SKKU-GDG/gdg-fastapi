from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
from pydub import AudioSegment
from vosk import Model, KaldiRecognizer

import json
import wave
import io
import os
import uuid
import shutil
# deepfake module
import video

app = FastAPI()

MODEL_PATH = "vosk-model-small-en-us-0.15"
model = Model(MODEL_PATH)

def convert_to_wav_bytes(audio_bytes: bytes, ext: str) -> io.BytesIO:
    audio = AudioSegment.from_file(io.BytesIO(audio_bytes), format=ext.strip('.'))
    audio = audio.set_channels(1)
    audio = audio.set_frame_rate(16000)
    wav_io = io.BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    return wav_io

def transcribe_audio_from_bytes(wav_bytes_io: io.BytesIO):
    wf = wave.open(wav_bytes_io, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() not in [8000, 16000, 32000, 44100, 48000]:
        raise ValueError("wav 파일은 16bit, mono, 8000~48000Hz 이어야 합니다.")

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    results = []

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            results.append(res)
    res = json.loads(rec.FinalResult())
    results.append(res)

    texts = [r.get('text', '') for r in results]
    return ' '.join(texts)

# ========================
# audio extraction
# ========================
@app.post("/upload")
async def upload_audio(file: UploadFile = File(...)):
    try:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".aac", ".mp4"]:
            return JSONResponse(
                content={"message": "Only .aac or .mp4 files are supported."},
                status_code=400
            )

        audio_bytes = await file.read()
        wav_io = convert_to_wav_bytes(audio_bytes, ext)
        transcription = transcribe_audio_from_bytes(wav_io)

        return JSONResponse(
            content={
                "message": "File received and transcribed successfully.",
                "filename": file.filename,
                "transcription": transcription
            },
            status_code=200
        )

    except Exception as e:
        print(e)
        return JSONResponse(
            content={"message": f"An error occurred: {str(e)}"},
            status_code=500
        )

# ========================
# Generate AI video
# ========================
@app.post("/get-video")
async def get_video(
    text: str = Form(...),
    video_file: Optional[UploadFile] = File(None)
):
    try:
        if video_file:
            temp_video_path = f"Wav2Lip/{uuid.uuid4()}_{video_file.filename}"
            with open(temp_video_path, "wb") as buffer:
                shutil.copyfileobj(video_file.file, buffer)
                
            video.clear_rotation_metadata(temp_video_path)
            
            result_path, temp_files = video.generate_video_from_text_and_video(text, temp_video_path)
            temp_files.append(temp_video_path)
        else:
            result_path, temp_files = video.generate_video_from_text(text)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Generated video not found")

    def file_iterator(path, temp_paths):
        with open(path, "rb") as f:
            yield from f
        for p in temp_paths:
            try:
                os.remove(p)
                print(f"[INFO] 삭제됨: {p}")
            except Exception as e:
                print(f"[WARN] 삭제 실패: {p} - {e}")

    return StreamingResponse(
        file_iterator(result_path, temp_files),
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={os.path.basename(result_path)}"}
    )
