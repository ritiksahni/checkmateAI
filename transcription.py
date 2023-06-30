import tempfile
import openai

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter


def main(videoId):
    transcript = YouTubeTranscriptApi.get_transcript(videoId)
    formatter = TextFormatter()
    formatted_text = formatter.format_transcript(transcript)

    with open("transcripts/" + videoId + "_transcript.txt", "w") as txt:
        txt.write(formatted_text)
    return formatted_text
