from enum import Enum

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    mp3 = "mp3"
    wav = "wav"


class PropertyAudioRequest(BaseModel):
    property_id: str = Field(min_length=1)
    audio_base64: str = Field(min_length=1)
    audio_format: AudioFormat


class AudioFacts(BaseModel):
    transcript: str
    category: str
    urgent: bool
    due_date: str | None = None


class PropertyAction(BaseModel):
    property_id: str
    transcript: str
    action: str
    priority: str
    due_date: str | None = None

