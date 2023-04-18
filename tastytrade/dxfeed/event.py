from abc import ABC


class Event(ABC):
    @classmethod
    def from_stream(cls, data: list) -> list['Event']:
        """
        Takes a list of raw trade data fetched by :class:`~tastyworks.streamer.DataStreamer`
        and returns a list of :class:`~tastyworks.dxfeed.event.Event` objects.

        :param data: list of raw quote data from streamer

        :return: list of :class:`~tastyworks.dxfeed.event.Event` objects from data
        """
        objs = []
        size = len(cls.__dataclass_fields__)
        multiples = len(data) / size
        if not multiples.is_integer():
            raise Exception('Mapper data input values are not an integer multiple of the key size')
        for i in range(int(multiples)):
            offset = i * size
            local_values = data[offset:(i + 1) * size]
            objs.append(cls(*local_values))
        return objs
