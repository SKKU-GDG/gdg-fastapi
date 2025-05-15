from gtts import gTTS
import librosa
import os
import cv2
import subprocess
import sys
import uuid
import shutil
import json

def generate_tts(text, output_path):
    tts = gTTS(text=text, lang='en')
    tts.save(output_path)
    
def get_audio_length(file_path):
    audio, sr = librosa.load(file_path, sr=None)
    length_in_seconds = librosa.get_duration(y=audio, sr=sr)
    return length_in_seconds

def create_video_from_image(image_path, output_video_path, video_length, fps):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"No image: {image_path}")

    height, width, _ = image.shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    total_frames = int(video_length * fps)
    for _ in range(total_frames):
        video_writer.write(image)

    video_writer.release()
    
def get_rotation(input_path: str) -> int:
    """ffprobe를 사용하여 회전 메타데이터 추출"""
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream_tags=rotate',
        '-of', 'json',
        input_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
    metadata = json.loads(result.stdout)
    rotate_tag = metadata.get('streams', [{}])[0].get('tags', {}).get('rotate', '0')
    return int(rotate_tag)

def clear_rotation_metadata(input_path: str):
    """영상의 회전 각도에 따라 적절히 회전시키고 메타데이터 제거"""
    rotation = get_rotation(input_path)
    print(f"[INFO] Detected rotation: {rotation} degrees")

    transpose_filter = None
    if rotation == 90:
        transpose_filter = 'transpose=1'   # 시계 방향 90도
    elif rotation == 180:
        transpose_filter = 'transpose=1,transpose=1'  # 두 번 회전
    elif rotation == 270:
        transpose_filter = 'transpose=2'   # 반시계 방향 90도

    temp_path = input_path + ".temp.mp4"
    command = ['ffmpeg', '-i', input_path]

    if transpose_filter:
        command += ['-vf', transpose_filter]

    command += [
        '-metadata:s:v:0', 'rotate=0',   # 메타데이터 제거
        '-c:a', 'copy',                  # 오디오 복사
        '-y',                            # 덮어쓰기
        temp_path
    ]

    subprocess.run(command, check=True)
    os.replace(temp_path, input_path)
# def clear_rotation_metadata(input_path: str):
#     temp_path = input_path + ".temp.mp4"
#     command = [
#         'ffmpeg',
#         '-i', input_path,
#         '-vf', 'transpose=0',   # 필요에 따라 transpose 값 조정 가능
#         #'-metadata:s:v:0', 'rotate=0',
#         temp_path
#     ]
#     subprocess.run(command, check=True)
#     os.replace(temp_path, input_path)
    

def generate_video_from_text(text: str) -> (str, list):
    uid = str(uuid.uuid4())
    basic_path = "Wav2Lip/"
    image_path = "example.png"
    output_tts_path = f"{uid}_audio.mp3"
    output_video_path = f"{uid}_video.mp4"
    checkpoint_path = "checkpoints/wav2lip_gan.pth"
    result_path = os.path.join(basic_path, "results", f"result_voice.mp4")
    fps = 25

    tts_full = os.path.join(basic_path, output_tts_path)
    video_full = os.path.join(basic_path, output_video_path)

    try:
        generate_tts(text, tts_full)
        length = get_audio_length(tts_full)
        create_video_from_image(image_path, video_full, length, fps)

        print(f"[INFO] Running Wav2Lip inference...")
        command = [
            sys.executable, 'inference.py',
            '--checkpoint_path', checkpoint_path,
            '--face', output_video_path,
            '--audio', output_tts_path
        ]
        subprocess.run(command, cwd=basic_path, check=True)
    except Exception as e:
        raise RuntimeError(f"Deepfake Generation failure: {e}")

    temp_files = [tts_full, video_full, result_path]

    if os.path.exists(result_path):
        return result_path, temp_files
    else:
        raise FileNotFoundError(f"No result video: {result_path}")


def generate_video_from_text_and_video(text: str, video_path: str) -> (str, list):
    uid = str(uuid.uuid4())
    basic_path = "Wav2Lip/"
    output_tts_path = f"{uid}_audio.mp3"
    video_filename = f"{uid}_face_input.mp4"
    checkpoint_path = "checkpoints/wav2lip_gan.pth"
    result_path = os.path.join(basic_path, "results", "result_voice.mp4")

    tts_full = os.path.join(basic_path, output_tts_path)   
    video_full = os.path.join(basic_path, video_filename)
    
    generate_tts(text, tts_full)
    shutil.copy(video_path, video_full)
    

    try:
        command = [
            sys.executable, 'inference.py',
            '--checkpoint_path', checkpoint_path,
            '--face', video_filename,
            '--audio', output_tts_path,
            '--static', 'True'
        ]
        subprocess.run(command, cwd=basic_path, check=True)
    except Exception as e:
        raise RuntimeError(f"Wav2Lip executing error: {e}")

    temp_files = [tts_full, video_full, result_path]

    if os.path.exists(result_path):
        return result_path, temp_files
    else:
        raise FileNotFoundError(f"No Wav2Lip result video: {result_path}")



#test code
# if __name__ == "__main__":
#     basic_path = "Wav2Lip/"
    
#     #tts
#     text = "Your voice matters"
#     output_tts_path = "input_audio.mp3"
#     generate_tts(text, basic_path + output_tts_path)
    
#     # #image video
#     # length = get_audio_length(basic_path + output_tts_path)    
#     # image_path = "example.jpg" 
#     # output_video_path = "input_video.mp4" 
#     # fps = 25
#     # create_video_from_image(image_path, basic_path + output_video_path, length, fps)

#     # given video  
#     output_video_path = "test.mp4" 

#     python_path = sys.executable
    
#     command = [
#         python_path, 'inference.py',
#         '--checkpoint_path',"checkpoints/wav2lip_gan.pth",
#         '--face', output_video_path,
#         '--audio', output_tts_path,
#         '--static', 'True' 
#     ]
    
#     subprocess.run(command, cwd='Wav2Lip', check=True)
    
    