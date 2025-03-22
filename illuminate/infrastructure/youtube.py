import os
import re
from pathlib import Path

# 개발 모드 여부
DEV_MODE = os.getenv('DEV_MODE', 'True').lower() in ('true', '1', 't')


class TranscriptNotFoundError(Exception):
    pass


def extract_video_id(url: str) -> str | None:
    """YouTube URL에서 비디오 ID를 추출합니다.

    Args:
        url (str): YouTube 비디오 URL

    Returns:
        str: 비디오 ID 또는 유효하지 않은 URL일 경우 None

    """
    # 정규 표현식 패턴들
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # 표준 및 임베드 URL
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # 짧은 URL
        r'(?:embed\/)([0-9A-Za-z_-]{11})',  # 임베드 URL
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_transcript(youtube_url: str) -> str:
    """YouTube URL에서 자막을 가져옵니다.

    현재는 YouTube API 연동을 제거하고 example.md 파일에서 예제 자막을 읽어옵니다.

    Args:
        youtube_url (str): YouTube 비디오 URL (현재는 URL 형식만 검증)

    Returns:
        str: 자막 텍스트

    Raises:
        ValueError: 올바르지 않은 YouTube URL
        TranscriptNotFoundException: 자막을 찾을 수 없는 경우
        Exception: 기타 오류 발생 시

    """
    video_id = extract_video_id(youtube_url)

    if not video_id:
        raise ValueError('올바른 유튜브 URL이 아닙니다.')

    try:
        return get_example_transcript()
    except Exception as e:
        raise TranscriptNotFoundException(f'자막을 가져올 수 없습니다: {e!s}')


def get_example_transcript() -> str:
    """example.md 파일에서 예제 자막을 읽어옵니다.

    Returns:
        str: 예제 자막 텍스트

    Raises:
        FileNotFoundError: example.md 파일을 찾을 수 없는 경우

    """
    # 현재 파일과 같은 디렉토리에 있는 example.md 파일 경로
    current_dir = Path(__file__).parent
    example_path = current_dir / 'example.md'

    # 파일 내용 읽기
    with open(example_path, encoding='utf-8') as f:
        return f.read()
