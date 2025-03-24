from pydantic import BaseModel


class TranscriptResponse(BaseModel):
    """YouTube 자막 응답 모델."""

    video_id: str
    transcript: str
