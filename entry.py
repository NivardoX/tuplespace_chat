import time
from dataclasses import dataclass

import nanoid


@dataclass
class Entry:
    unique_id: str = nanoid.generate()
    created_at: int = int(time.time())

    type: str = "message"
    target: str = None
    source: str = None
    room: str = None
    message: str = None

    tuple_space_fields = ["type", "room", "target", "source"]

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    def equals(self, other: object) -> object:

        for key in self.tuple_space_fields:
            is_self_prop_none = getattr(self, key) is None
            is_other_prop_none = getattr(other, key) is None
            are_props_different = getattr(other, key) != getattr(self, key)

            if not is_self_prop_none and not is_other_prop_none and are_props_different:
                return False
        return True
