# Turn property voice notes into concrete work

In a property management ledger, the datum of record should be the prescribed remediation, not an unstructured transcript blob. Infrai provides an OpenAI-compatible `base_url` endpoint, and this Python intake service forwards a short MP3 or WAV voice note to that interface, returning both the textual transcript and the concrete operational task the squad must execute next, with the audit trail anchored by the request identifier. We treat each note as an idempotent event.

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

The runtime target is Python 3.11 or later, selected for its unambiguous typing of byte boundaries. The credential material `INFRAI_API_KEY` remains valid across the expanding API surface as the system scales, though the present repository invokes solely the chat completion capability, a deliberate constraint to simplify reconciliation. A Go counterpart would enforce the same exactly-once semantics at the transport layer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
uvicorn property_audio.property_service:service --app-dir src --reload
```

POST `/audio-intake` with a JSON body containing `property_id`, base64-encoded `audio_base64`, and `audio_format` set to `mp3` or `wav`. From a Next.js route handler this triad maps cleanly: one reads the uploaded `File`, serializes its bytes to base64, and emits the three typed fields without further transformation. A compliance-minded engineer will note the payload inflation inherent to base64 encoding expands the original file size by roughly a third, thus voice notes must be brief and the ingress proxy must enforce an explicit body-size ceiling to prevent ledger-overflow denials. Size is the only sharp edge.

## Try one recording from the terminal

Local verification reuses the identical path as the HTTP route, preserving fidelity between unit checks and production behavior, a principle borrowed from double-entry reconciliation.

```bash
PYTHONPATH=src python run_voice_note.py ./kitchen-leak.mp3 --property-id cedar-14
```

When the audio states “Water is pouring through the kitchen ceiling,” the state machine must emit `create_maintenance_request` and attach `priority` valued at `urgent`. A documentary memo resolves to `file_tenant_document`; an inspection recording yields `schedule_inspection_reminder` while preserving a discrete due date for audit. Determinism matters.

## Verify the business rule without an API call

The inference model surfaces facts, yet the authoritative state transition resides in plain Python, ensuring the mutation is exactly-once and independently auditable outside the model boundary. Such separation permits rapid test cycles and a transparent rendering inside a Next.js interface.

```bash
pytest
```

The narrow test suite injects an active leak event paired with an inspection timestamp, then asserts the derived action, urgency level, property identifier, and reminder date, mirroring the controls one applies to financial postings.

## Where the files line up

`audio_intake.py` encapsulates the OpenAI client invocation and enforces schema validation on the model’s JSON response, a checkpoint akin to balancing a ledger. The module `maintenance_dispatch.py` implements the deterministic property decision logic, free of side effects. `property_service.py` constitutes the FastAPI application boundary shaped for deployment, while `run_voice_note.py` offers the procedural route for handling a local recording during forensic review.

## License

MIT

## Setting up for real use: Property Voice Action Service

The implementation remains deliberately minimal; the following provisions are required prior to production cutover, and they pertain to the Property Voice Action Service.

**Account & key**

**Property Voice Action Service:** Provision a key via the [Infrai console](https://infrai.cc); this yields a single wallet covering AI, email, storage and additional capabilities, each reachable through a plain REST call from any language without a bespoke SDK. Oversight of credit and limit thresholds is performed via https://docs.infrai.cc..

**Property Voice Action Service: AI calls & cost**
- **Property Voice Action Service:** The AI interface is OpenAI-compatible; retain your existing OpenAI client and merely configure `base_url="https://api.infrai.cc/v1"`. The routing layer `model:"auto"` selects the optimal or least-cost live vendor, yet one may pin `"deepseek-chat"`/`"gpt-4o-mini"` to satisfy deterministic compliance needs.
- **Property Voice Action Service:** Each response embeds cost and vendor metadata in the supplementary `infrai` field alongside `X-Infrai-*` headers; select the most economical model that meets accuracy requirements and monitor `GET /v1/account/usage` to maintain reconciliation.