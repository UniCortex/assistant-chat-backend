from dataclasses import dataclass


@dataclass
class Entity:
    """Marker base class for all domain entities.

    Entities have identity and mutable state unlike value objects.
    """
