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
        """
        TX_PENDING is an indicator of pending transactional update.
        When txPending is true it means, that an ongoing transaction update that spans
        multiple events is in process. All events with txPending true shall be put into
        a separate pending list for each source id and should be processed later when
        an event for this source id with txPending false comes.
        """
        return self.event_flags & TX_PENDING != 0

    @property
    def remove(self) -> bool:
        """
        REMOVE_EVENT is used to indicate that that the event with the corresponding
        index has to be removed.
        """
        return self.event_flags & REMOVE_EVENT != 0

    @property
    def snapshot_begin(self) -> bool:
        """
        SNAPSHOT_BEGIN is used to indicate when the loading of a snapshot starts.
        Snapshot load starts on new subscription and the first indexed event that
        arrives for each non-zero source id on new subscription may have snapshotBegin
        set to true. It means, that an ongoing snapshot consisting of multiple events is
        incoming. All events for this source id shall be put into a separate pending
        list for each source id.
        """
        return self.event_flags & SNAPSHOT_BEGIN != 0

    @property
    def snapshot_end(self) -> bool:
        """
        SNAPSHOT_END or SNAPSHOT_SNIP are used to indicate the end of a snapshot.
        The last event of a snapshot is marked with either snapshotEnd or snapshotSnip.
        At this time, all events from a pending list for the corresponding source can be
        processed, unless txPending is also set to true. In the later case, the
        processing shall be further delayed due to ongoing transaction.

        The difference between snapshotEnd and snapshotSnip is the following:
        snapshotEnd indicates that the data source had sent all the data pertaining to
        the subscription for the corresponding indexed event, while snapshotSnip
        indicates that some limit on the amount of data was reached and while there
        still might be more data available, it will not be provided.
        """
        return self.event_flags & SNAPSHOT_END != 0

    @property
    def snapshot_mode(self) -> bool:
        """
        SNAPSHOT_MODE is used to instruct dxFeed to use snapshot mode. It is intended to
        be used only for publishing to activate (if not yet activated) snapshot mode.
        The difference from SNAPSHOT_BEGIN flag is that SNAPSHOT_MODE only switches on
        snapshot mode without starting snapshot synchronization protocol.
        When a snapshot is empty or consists of a single event, then the event can have
        both snapshotBegin and snapshotEnd or snapshotSnip flags. In case of an empty
        snapshot, removeEvent on this event is also set to true.
        """
        return self.event_flags & SNAPSHOT_MODE != 0

    @property
    def snapshot_snip(self) -> bool:
        """
        SNAPSHOT_END or SNAPSHOT_SNIP are used to indicate the end of a snapshot.
        The last event of a snapshot is marked with either snapshotEnd or snapshotSnip.
        At this time, all events from a pending list for the corresponding source can be
        processed, unless txPending is also set to true. In the later case, the
        processing shall be further delayed due to ongoing transaction.

        The difference between snapshotEnd and snapshotSnip is the following:
        snapshotEnd indicates that the data source had sent all the data pertaining to
        the subscription for the corresponding indexed event, while snapshotSnip
        indicates that some limit on the amount of data was reached and while there
        still might be more data available, it will not be provided.
        """
        return self.event_flags & SNAPSHOT_SNIP != 0
