from typing import Any, List

from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from pydantic.alias_generators import to_camel

from tastytrade import logger
from tastytrade.utils import TastytradeError

REMOVE_EVENT = 0x2
SNAPSHOT_BEGIN = 0x4
SNAPSHOT_END = 0x8
SNAPSHOT_MODE = 0x40
SNAPSHOT_SNIP = 0x10
TX_PENDING = 0x1


class Event(BaseModel):
    """
    Base class for dxfeed events received from the data streamer.
    """

    #: symbol of this event
    event_symbol: str
    #: time of this event
    event_time: int

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    @field_validator("*", mode="before")
    @classmethod
    def change_nan_to_none(cls, v: Any) -> Any:
        if v in {"NaN", "Infinity", "-Infinity"}:
            return None
        return v

    @classmethod
    def from_stream(cls, data: list) -> List["Event"]:
        """
        Makes a list of event objects from a list of raw trade data fetched by
        a :class:`~tastyworks.streamer.DXFeedStreamer`.

        :param data: list of raw quote data from streamer

        :return: list of event objects from data
        """
        objs = []
        size = len(cls.model_fields)
        multiples = len(data) / size
        if not multiples.is_integer():
            raise TastytradeError(
                "Mapper data input values are not a multiple of the key size!"
            )
        keys = cls.model_fields.keys()
        for i in range(int(multiples)):
            offset = i * size
            local_values = data[offset : (i + 1) * size]
            event_dict = dict(zip(keys, local_values))
            try:
                objs.append(cls(**event_dict))
            except ValidationError as e:
                # we just skip these events as they're generally not helpful
                logger.debug(f"Skipping event due to error: {e}")
        return objs


class IndexedEvent(Event):
    """
    A dxfeed `IndexedEvent` with flags computed bitwise.
    For info see `here <https://docs.dxfeed.com/dxfeed/api/com/dxfeed/event/IndexedEvent.html>`_.
    """

    #: flags for the event
    event_flags: int

    @property
    def pending(self) -> bool:
        return self.event_flags & TX_PENDING != 0

    @property
    def remove(self) -> bool:
        return self.event_flags & REMOVE_EVENT != 0

    @property
    def snapshot_begin(self) -> bool:
        return self.event_flags & SNAPSHOT_BEGIN != 0

    @property
    def snapshot_end(self) -> bool:
        return self.event_flags & SNAPSHOT_END != 0

    @property
    def snapshot_mode(self) -> bool:
        return self.event_flags & SNAPSHOT_MODE != 0

    @property
    def snapshot_snip(self) -> bool:
        return self.event_flags & SNAPSHOT_SNIP != 0
