from fastapi import FastAPI, HTTPException
from openai import APIConnectionError, APIStatusError, RateLimitError

from .audio_intake import transcribe_and_dispatch
from .models import PropertyAction, PropertyAudioRequest


service = FastAPI(title="Property audio intake")


@service.post("/audio-intake", response_model=PropertyAction)
def audio_intake(request: PropertyAudioRequest) -> PropertyAction:
    try:
        return transcribe_and_dispatch(request)
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="Audio processing is busy; retry later") from exc
    except APIStatusError as exc:
        status = exc.status_code if 400 <= exc.status_code < 500 else 502
        raise HTTPException(status_code=status, detail="Audio request was rejected") from exc
    except (APIConnectionError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Audio processing did not complete") from exc

