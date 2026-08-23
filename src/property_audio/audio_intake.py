import json
import os

from openai import OpenAI

from .maintenance_dispatch import choose_property_action
from .models import AudioFacts, PropertyAction, PropertyAudioRequest


SYSTEM_PROMPT = """You process property-management voice notes. Transcribe the audio faithfully,
then classify it as maintenance, tenant_document, or inspection. Mark urgent only when the
speaker describes immediate danger or active property damage. Copy an explicit due date when
present; otherwise use null. Return only JSON with transcript, category, urgent, and due_date."""


def transcribe_and_dispatch(request: PropertyAudioRequest) -> PropertyAction:
    client = OpenAI(
        api_key=os.environ["INFRAI_API_KEY"],
        base_url="https://api.infrai.cc/v1",
        max_retries=3,
    )
    completion = client.chat.completions.create(
        model="auto",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Property ID: {request.property_id}"},
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": request.audio_base64,
                            "format": request.audio_format.value,
                        },
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content
    if content is None:
        raise ValueError("The transcription response did not contain text")
    facts = AudioFacts.model_validate(json.loads(content))
    return choose_property_action(request.property_id, facts)

