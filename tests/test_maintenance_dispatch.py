from property_audio.maintenance_dispatch import choose_property_action
from property_audio.models import AudioFacts


def test_active_leak_becomes_an_urgent_maintenance_request() -> None:
    facts = AudioFacts(
        transcript="Water is pouring through the kitchen ceiling.",
        category="maintenance",
        urgent=True,
    )

    action = choose_property_action("cedar-14", facts)

    assert action.action == "create_maintenance_request"
    assert action.priority == "urgent"
    assert action.property_id == "cedar-14"


def test_inspection_keeps_its_due_date() -> None:
    facts = AudioFacts(
        transcript="Remind me to inspect unit 3 on 2026-09-02.",
        category="inspection",
        urgent=False,
        due_date="2026-09-02",
    )

    action = choose_property_action("maple-court", facts)

    assert action.action == "schedule_inspection_reminder"
    assert action.due_date == "2026-09-02"

