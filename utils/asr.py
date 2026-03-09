import whisper
import os
import tempfile
import soundfile as sf
import numpy as np
from pydub import AudioSegment
import streamlit as st

ffmpeg_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ffmpeg-8.0.1-essentials_build', 'bin')
ffmpeg_path = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
ffprobe_path = os.path.join(ffmpeg_dir, 'ffprobe.exe')

# Add ffmpeg to system PATH for pydub
os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")

# Configure pydub
AudioSegment.converter = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

# ===============================
# Cached Whisper Model
# ===============================
@st.cache_resource
def load_whisper_model():
    print("Loading Whisper model (first time)...")
    return whisper.load_model("base")


def transcribe_audio(audio_file):
    """
    Transcribe audio file using Whisper.
    """

    try:

        filename = audio_file.name if hasattr(audio_file, 'name') else "temp_audio.wav"
        ext = os.path.splitext(filename)[1].lower() if filename else '.wav'

        temp_dir = tempfile.gettempdir()
        temp_input_path = os.path.join(temp_dir, filename)

        with open(temp_input_path, "wb") as f:
            buffer = audio_file.getbuffer() if hasattr(audio_file, 'getbuffer') else audio_file.read()
            f.write(buffer)

        audio_data = None
        sr = None

        try:
            audio_data, sr = sf.read(temp_input_path)

        except Exception:

            audio = AudioSegment.from_file(temp_input_path)

            if audio.channels > 1:
                audio = audio.set_channels(1)

            audio = audio.set_frame_rate(16000)

            audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32)
            sr = audio.frame_rate

            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val

        if len(audio_data.shape) > 1:
            audio_data = np.mean(audio_data, axis=1)

        audio_16bit = np.int16(audio_data * 32767)

        wav_output_path = os.path.join(temp_dir, "whisper_input.wav")

        from scipy.io import wavfile
        wavfile.write(wav_output_path, sr, audio_16bit)

        original_path = os.environ.get('PATH', '')
        os.environ['PATH'] = ffmpeg_dir + os.pathsep + original_path

        try:
            model = load_whisper_model()
            result = model.transcribe(wav_output_path)
        finally:
            os.environ['PATH'] = original_path

        return result["text"]

    finally:

        try:
            if 'temp_input_path' in locals() and os.path.exists(temp_input_path):
                os.remove(temp_input_path)
        except:
            pass

        try:
            if 'wav_output_path' in locals() and os.path.exists(wav_output_path):
                os.remove(wav_output_path)
        except:
            pass