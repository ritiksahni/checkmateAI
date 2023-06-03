import tempfile
import openai

from moviepy.editor import *
from pytube import YouTube
from urllib.parse import urlparse, parse_qs


def transcribe_audio(fpath):
    fsize = os.path.getsize(fpath)
    fsize_mb = fsize / (1024 * 1024)
    if fsize_mb < 25:
        with open(fpath, "rb") as audiofile:
            transcript = openai.Audio.transcribe("whisper-1", audiofile)
        return transcript
    else:
        return "Audio file size exceeds the limit (25mb)."


def main(url):
    query = urlparse(url).query
    params = parse_qs(query)
    videoId = params["v"][0]

    with tempfile.TemporaryDirectory() as tempDir:
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_stream.download(output_path=tempDir)
        # Convert audio to mp3.
        audio_path = os.path.join(tempDir, audio_stream.default_filename)
        audio_clip = AudioFileClip(audio_path)
        audio_clip.write_audiofile(os.path.join(tempDir, f"{videoId}.mp3"))

        audio_path = f"{tempDir}/{videoId}.mp3"

        transcript = transcribe_audio(audio_path)
        os.remove(audio_path)

        return transcript.text
