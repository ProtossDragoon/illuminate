import re
from pathlib import Path

import dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter, TextFormatter

dotenv.load_dotenv()
ytt_api = YouTubeTranscriptApi()


class InvalidYoutubeURLError(Exception): ...


def extract_video_id(url: str) -> str | None:
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise InvalidYoutubeURLError(url)


def get_example_transcript() -> str:
    current_dir = Path(__file__).parent
    example_path = current_dir / 'example.srt'

    with example_path.open(encoding='utf-8') as f:
        return f.read()


def get_transcript(youtube_url: str, fmt: str = 'srt') -> str:
    video_id = extract_video_id(youtube_url)
    transcript_data = ytt_api.fetch(video_id, languages=['ko', 'en'])

    if fmt.lower() == 'text':
        return TextFormatter().format_transcript(transcript_data)
    return SRTFormatter().format_transcript(transcript_data)
