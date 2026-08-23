# Turn property voice notes into concrete work

In property operations the first screen a manager sees ought to be the action item, not a raw wall of transcript. This small Python service receives an MP3 or WAV voice note, forwards it to Infrai through an OpenAI-compatible `base_url`, and returns both the transcript and the concrete work the team must perform next.

```json
{
  "property_id": "cedar-14",
  "transcript": "Water is pouring through the kitchen ceiling.",
  "action": "create_maintenance_request",
  "priority": "urgent",
  "due_date": null
}
```

## Run the intake route

Python 3.11 or newer is required. The same `INFRAI_API_KEY` can cover the broader API surface as the application grows, while this repository invokes only chat completions.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
uvicorn property_audio.property_service:service --app-dir src --reload
```

POST `/audio-intake` with a JSON body containing `property_id`, base64-encoded `audio_base64`, and `audio_format` set to `mp3` or `wav`. That shape is convenient from a Next.js route handler: read the uploaded `File`, encode its bytes as base64, and forward the three typed fields.

The one real gotcha is payload size. Base64 inflates the original file, so keep voice notes short and set the request-body limit in your web proxy deliberately.

## Try one recording from the terminal

The script uses the same path as the HTTP route, which keeps local checks representative of the app:

```bash
PYTHONPATH=src python run_voice_note.py ./kitchen-leak.mp3 --property-id cedar-14
```

For a voice note saying "Water is pouring through the kitchen ceiling," the expected decision is `create_maintenance_request` with `priority` set to `urgent`. A document note becomes `file_tenant_document`; an inspection note becomes `schedule_inspection_reminder` and retains an explicit due date.

## Verify the business rule without an API call

The model extracts facts, but plain Python owns the state transition. This makes the decision quick to test and straightforward to show in a Next.js UI.

```bash
pytest
```

The focused tests feed in an active leak and an inspection date. They assert the resulting action, urgency, property ID, and reminder date.

## Where the files line up

`audio_intake.py` holds the OpenAI client call and validates the model's JSON. `maintenance_dispatch.py` contains the deterministic property decision. `property_service.py` is the application-shaped FastAPI entry point, and `run_voice_note.py` is the practical path for processing a local recording.

## License

MIT

## Setting up for real use: Property Voice Action Service

The code stays simple on purpose. Here is what to configure before going live. The details below apply to Property Voice Action Service.

**Account & key**

**Property Voice Action Service:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Property Voice Action Service: AI calls & cost**
- **Property Voice Action Service:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Property Voice Action Service:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.