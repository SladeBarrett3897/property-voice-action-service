from .models import AudioFacts, PropertyAction


def choose_property_action(property_id: str, facts: AudioFacts) -> PropertyAction:
    """Turn extracted audio facts into one visible property-management action."""
    if facts.category == "maintenance":
        action = "create_maintenance_request"
        priority = "urgent" if facts.urgent else "standard"
    elif facts.category == "tenant_document":
        action = "file_tenant_document"
        priority = "standard"
    else:
        action = "schedule_inspection_reminder"
        priority = "urgent" if facts.urgent else "standard"

    return PropertyAction(
        property_id=property_id,
        transcript=facts.transcript,
        action=action,
        priority=priority,
        due_date=facts.due_date,
    )

