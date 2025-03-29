from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel

from illuminate.infrastructure.notion import get_povs
from illuminate.infrastructure.youtube import (
    extract_video_id,
    get_example_transcript,
    get_transcript,
)
from illuminate.log_utils import setup_logging
from illuminate.service import summarizer

router = APIRouter()


class TranscriptResponse(BaseModel):
    """YouTube 자막 응답 모델."""

    video_url: str
    video_id: str
    transcript: str


def get_summerizer():
    return summarizer


@router.get('/transcript', response_model=TranscriptResponse)
async def get_transcript_endpoint(
    youtube_url: str = Query(..., description='YouTube 비디오 URL'),
    fmt: str = Query('text', description='자막 포맷 (srt 또는 text)'),
):
    """YouTube 비디오 URL에서 자막을 추출합니다."""
    try:
        video_id = extract_video_id(youtube_url)
        transcript_text = get_transcript(youtube_url, fmt=fmt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return TranscriptResponse(video_url=youtube_url, video_id=video_id, transcript=transcript_text)


@router.post('/summarize')
async def summarize(background_tasks: BackgroundTasks, summerizer=Depends(get_summerizer)):
    try:
        povs = get_povs()
        background_tasks.add_task(summerizer, get_example_transcript(), povs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    return 'ok'


if __name__ == '__main__':
    setup_logging()
