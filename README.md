# Gap Ear Backend

> Backend API for the Gap Ear assistive pronunciation training application.

-----

## ⚙️ Project Overview

This backend application, built with **FastAPI**, serves as the API endpoint for the Gap Ear Flutter frontend. It receives audio/video recordings and text input from the frontend, utilizes the **Vosk** module for speech-to-text conversion, and leverages the Gemini API to analyze pronunciation differences and provide feedback. For visual guidance in video mode, the application integrates the **Wav2Lip** module to generate deepfake videos.

## 🛠️ Technology Stack

  * **FastAPI:** A modern, high-performance Python web framework for building APIs.
  * **Vosk:** An open-source speech recognition toolkit for transcribing user audio into text, optimized for pronunciation recognition.
  * **Gemini API:** To analyze the differences between the target sentence and the recognized text, and to generate pronunciation advice.
  * **Wav2Lip:** A deep learning model for generating realistic lip synchronization in videos, providing visual pronunciation guidance.

## Endpoints

The following API endpoints are available:

  * **/upload (POST):**
      * Accepts `multipart/form-data` containing:
          * `media`: The user's voice recording (AAC) or video recording (MP4).
      * Converts the received media into WAV format.
      * Transcribes the audio from the WAV file using the **Vosk** module.
      * Returns a JSON response containing:
          * `recognized_text`: The text transcribed by the **Vosk** module.

  * **/get-video (POST):**
      * Accepts `multipart/form-data` containing:
          * `text` (Form parameter): The target sentence for lip-sync generation.
          * `video_file` (Optional File parameter): An MP4 video file to be used as the base for lip-syncing. If not provided, a default face model might be used.
      * If `video_file` is provided:
          * Saves the uploaded video file temporarily.
          * Clears any rotation metadata from the video file.
          * Utilizes the **Wav2Lip** module to generate a deepfake video with the provided `text` lip-synced to the audio of the `video_file`.
      * If `video_file` is not provided:
          * Utilizes the **Wav2Lip** module to generate a deepfake video of a default face model speaking the provided `text`.
      * Returns a JSON response containing:
          * `video_url`: URL or path to the generated deepfake video file.

## ⚙️ Setup and Deployment

To set up and deploy the backend application, follow these steps:

### Prerequisites

  * Python 3.x
  * pip (Python package installer)
  * FastAPI and Uvicorn (ASGI server)
  * Vosk model files for the desired language.
  * PyTorch and other dependencies for Wav2Lip.
  * A Gemini API key.

check ```requirements.txt``` file

### Installation

1.  Clone the backend repository (replace with the actual repository URL):

    ```bash
    git clone https://github.com/SKKU-GDG/gdg-fastapi
    cd gdg-fastapi
    ```

2.  Create a virtual environment (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    Ensure `fastapi`, `uvicorn`, `python-multipart`, `vosk`, `torch`, `torchvision`, and dependencies for `wav2lip` are included in your `requirements.txt`.

4.  Download Necessary Models and Checkpoints:

    To utilize the deepfake video generation functionalities, you need to download the appropriate models and checkpoints.


    * **Wav2Lip Checkpoints:** Download the following checkpoints required for the Wav2Lip module. You can use the following commands in your terminal within the backend directory:

        ```bash
        mkdir -p Wav2Lip/checkpoints && \
        gdown [https://drive.google.com/uc?export=download&id=1ZQwe70j4l6qZ4ea4ERFFLxTZoyK-21hb](https://drive.google.com/uc?export=download&id=1ZQwe70j4l6qZ4ea4ERFFLxTZoyK-21hb) -O Wav2Lip/checkpoints/wav2lip_gan.pth && \
        mkdir -p Wav2Lip/face_detection/detection/sfd && \
        gdown [https://drive.google.com/uc?export=download&id=1bTfcdIBbQT1ipbbZ-mzarP_Mq0MSuOP5](https://drive.google.com/uc?export=download&id=1bTfcdIBbQT1ipbbZ-mzarP_Mq0MSuOP5) -O Wav2Lip/face_detection/detection/sfd/s3fd.pth
        ```

        These commands will download:

        * `wav2lip_gan.pth`: The main Wav2Lip model checkpoint, saved in `Wav2Lip/checkpoints/`.
        * `s3fd.pth`: The face detection model checkpoint required by Wav2Lip, saved in `Wav2Lip/face_detection/detection/sfd/`.

5.  Configure Environment Variables:

    Create a `.env` file in the backend root directory and add your Gemini API key:

    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    ```

    You might need to configure paths to the Vosk model and Wav2Lip checkpoints as well, depending on your implementation.

### Running Locally

To run the backend application locally:

```bash
uvicorn main:app --reload
```

Replace `main` with the name of your main FastAPI application file. The backend will typically start on `http://127.0.0.1:8000`.

### Deployment

Deployment steps will vary depending on your chosen platform (e.g., Docker, cloud providers like AWS, Google Cloud, Azure, or platforms like Render). Ensure your deployment process includes:

  * Installing all necessary dependencies, including Vosk and Wav2Lip.
  * Downloading and configuring the Vosk model.
  * Configuring the Gemini API key as an environment variable.
  * Setting up the necessary infrastructure for video processing if using Wav2Lip.

## 🛠️ How It Works

1.  The Flutter frontend sends an audio or video recording and the target sentence to the `/upload` endpoint.
2.  The FastAPI backend receives the data.
3.  The backend uses the **Vosk** module to transcribe the audio from the received **audio (AAC) or video (MP4)** file. The video file's audio track is extracted for transcription.
4.  **Asynchronously**, the **/upload** endpoint returns a JSON response containing the `recognized_text`.
5.  **Concurrently**, the `recognized_text` from Vosk and the original `text` are sent to the Gemini API for pronunciation difference analysis and advice generation.
6.  **Asynchronously**, if the Flutter frontend sends a request to the **/get-video** endpoint with a `text` and an optional `video_file`:
      * The backend (specifically the `/get-video` endpoint) utilizes the **Wav2Lip** module, along with the provided `text` and the audio from the `video_file` (if provided, otherwise a default face is used), to generate a deepfake video showing synchronized lip movements. This process is computationally intensive. The URL or path to the generated video is then prepared for the response.

