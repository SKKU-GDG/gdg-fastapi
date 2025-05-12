from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
import os
import shutil
import uuid
import video

app = FastAPI()

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
            
            result_path, temp_files = video.generate_video_from_text_and_video(text, temp_video_path)
            temp_files.append(temp_video_path)

        else:
            # 텍스트만 기반으로 생성
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
