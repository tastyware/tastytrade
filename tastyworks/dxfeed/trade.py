import datetime

from tastyworks.dxfeed.mapped_item import MappedItem


class Trade(MappedItem):
    DXFEED_TEXT = 'Trade'

    def _process_fields(self, data_dict: dict):
        data_dict['time'] = datetime.datetime.fromtimestamp(data_dict['time'] / 1000_000_000)
        return data_dict

    def __init__(self, data=None):
        super().__init__(data=data)
