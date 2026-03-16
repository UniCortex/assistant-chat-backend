from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Marker base class for all value objects.

    All value objects are immutable (frozen=True) and compared by value.
    """
